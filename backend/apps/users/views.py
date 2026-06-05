from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from common.permissions import IsOwnerAdminManager

from . import auth_services
from .models import ClientProfile, StaffProfile
from .serializers import (
    ClientProfileSerializer,
    GoogleAuthSerializer,
    PhoneEmailTokenObtainPairSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
    PhoneAuthRequestSerializer,
    PhoneAuthVerifySerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    StaffProfileSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsOwnerAdminManager]
    search_fields = ["username", "email", "phone", "first_name", "last_name"]
    ordering_fields = ["id", "date_joined", "role"]


class ClientProfileViewSet(viewsets.ModelViewSet):
    queryset = ClientProfile.objects.select_related("user").all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER"}:
            return queryset
        return queryset.filter(user=self.request.user)


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.select_related("user").all()
    serializer_class = StaffProfileSerializer
    permission_classes = [IsOwnerAdminManager]


class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        request=GoogleAuthSerializer,
        description="Google OAuth login/register endpoint. Client sends Google ID token, backend verifies it, creates or links user, returns JWT tokens.",
        examples=[
            OpenApiExample(
                "Google id_token",
                value={"id_token": "eyJhbGciOiJSUzI1NiIs..."},
                request_only=True,
            ),
            OpenApiExample(
                "JWT response",
                value={
                    "access": "...",
                    "refresh": "...",
                    "user": {
                        "id": 1,
                        "email": "client@example.com",
                        "phone": None,
                        "first_name": "Ainara",
                        "last_name": "T",
                        "role": "CLIENT",
                        "has_client_profile": True,
                    },
                },
                response_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(description="JWT tokens and user payload."),
            400: OpenApiResponse(description="Invalid request or unverified Google email."),
            401: OpenApiResponse(description="Invalid token or audience mismatch."),
            503: OpenApiResponse(description="Google auth service unavailable."),
        },
    )
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = auth_services.login_with_google(serializer.validated_data["id_token"])
        except auth_services.GoogleEmailNotVerified as exc:
            return Response({"detail": str(exc), "code": exc.default_code}, status=400)
        except auth_services.GoogleAudienceMismatch as exc:
            return Response({"detail": str(exc), "code": exc.default_code}, status=401)
        except auth_services.GoogleTokenInvalid as exc:
            return Response({"detail": str(exc), "code": exc.default_code}, status=401)
        except auth_services.GoogleAuthServiceUnavailable as exc:
            return Response({"detail": str(exc), "code": exc.default_code}, status=503)
        return Response(payload)


class PhoneEmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneEmailTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        request=RegisterSerializer,
        responses={201: OpenApiResponse(description="JWT tokens and user payload.")},
        description="Register a CLIENT account with email/password and optional Kyrgyz phone number. Password is validated with Django password validators.",
        examples=[
            OpenApiExample(
                "Register client",
                value={
                    "email": "client@example.com",
                    "phone": "+996700111222",
                    "password": "StrongPass123",
                    "first_name": "Ainara",
                    "last_name": "T",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": auth_services.build_user_payload(user),
            },
            status=201,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        request=LogoutSerializer,
        responses={204: OpenApiResponse(description="Refresh token blacklisted.")},
        description="Blacklist a refresh token.",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = RefreshToken(serializer.validated_data["refresh"])
        token.blacklist()
        return Response(status=204)


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        request=PasswordChangeSerializer,
        responses={204: OpenApiResponse(description="Password changed."), 400: OpenApiResponse(description="Invalid old password.")},
        description="Change password for a password-based account.",
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"user": request.user})
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "Old password is incorrect."}, status=400)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response(status=204)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        request=PasswordResetRequestSerializer,
        responses={200: OpenApiResponse(description="Password reset email sent if account exists.")},
        description="Request a password reset email. Response is intentionally identical for existing and missing accounts.",
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_services.request_password_reset(serializer.validated_data["email"])
        return Response({"detail": "If the email exists, reset instructions were sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        request=PasswordResetConfirmSerializer,
        responses={204: OpenApiResponse(description="Password reset complete."), 400: OpenApiResponse(description="Invalid token.")},
        description="Confirm password reset with uid/token from email.",
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            auth_services.confirm_password_reset(**serializer.validated_data)
        except auth_services.GoogleTokenInvalid:
            return Response({"detail": "Invalid password reset token."}, status=400)
        return Response(status=204)


class PhoneAuthRequestCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        request=PhoneAuthRequestSerializer,
        responses={200: OpenApiResponse(description="SMS code sent via configured provider. Console provider prints it to terminal.")},
        description="Request a 6-digit phone login code for a Kyrgyz phone number. Local console provider logs the code in terminal.",
        examples=[OpenApiExample("Kyrgyz phone", value={"phone": "+996700111222"}, request_only=True)],
    )
    def post(self, request):
        serializer = PhoneAuthRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_services.request_phone_login_code(serializer.validated_data["phone"])
        return Response({"detail": "If the phone is valid, an authentication code was sent."})


class PhoneAuthVerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        request=PhoneAuthVerifySerializer,
        responses={
            200: OpenApiResponse(description="JWT tokens and user payload."),
            400: OpenApiResponse(description="Invalid, expired or exhausted phone code."),
        },
        description="Verify a 6-digit phone code. Creates a CLIENT account and ClientProfile when the phone is new.",
        examples=[OpenApiExample("Verify code", value={"phone": "+996700111222", "code": "123456"}, request_only=True)],
    )
    def post(self, request):
        serializer = PhoneAuthVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = auth_services.verify_phone_login_code(**serializer.validated_data)
        except auth_services.PhoneAuthError as exc:
            return Response({"detail": str(exc), "code": exc.default_code}, status=400)
        return Response(payload)
