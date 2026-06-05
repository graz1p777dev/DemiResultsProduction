from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from common.validators import kyrgyz_phone_validator

from .models import ClientProfile, StaffProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "google_id",
            "role",
            "is_active",
            "is_2fa_enabled",
        ]
        read_only_fields = ["id", "google_id", "is_2fa_enabled"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ClientProfileSerializer(serializers.ModelSerializer):
    purchase_count = serializers.IntegerField(source="user.client_sales.count", read_only=True)
    order_count = serializers.IntegerField(source="user.orders.count", read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            "id",
            "user",
            "birth_date",
            "gender",
            "skin_type",
            "skin_concerns",
            "allergies",
            "complaints",
            "contraindications",
            "current_routine",
            "previous_treatments",
            "ai_summary",
            "telegram_username",
            "recommendations",
            "staff_notes",
            "notes",
            "total_orders",
            "total_spent",
            "created_at",
            "updated_at",
            "purchase_count",
            "order_count",
        ]
        read_only_fields = ["created_at", "updated_at"]


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = "__all__"


class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(trim_whitespace=True, allow_blank=False, required=True)


class PhoneEmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login = attrs.get(self.username_field)
        if login:
            user = (
                User.objects.filter(email__iexact=login).first()
                or User.objects.filter(phone=login).first()
                or User.objects.filter(username=login).first()
            )
            if user:
                attrs[self.username_field] = user.get_username()
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=True, allow_blank=False, required=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate_new_password(self, value):
        validate_password(value, user=self.context.get("user"))
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class PhoneAuthRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, validators=[kyrgyz_phone_validator], trim_whitespace=True)


class PhoneAuthVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, validators=[kyrgyz_phone_validator], trim_whitespace=True)
    code = serializers.RegexField(regex=r"^\d{6}$", required=True)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=False, allow_blank=True, validators=[kyrgyz_phone_validator], trim_whitespace=True)

    class Meta:
        model = User
        fields = ["id", "email", "phone", "password", "first_name", "last_name"]
        read_only_fields = ["id"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        return value.lower()

    def validate_phone(self, value):
        return value or None

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data["email"]
        base_username = email.split("@", 1)[0]
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}{suffix}"
        user = User.objects.create_user(
            username=username,
            password=password,
            role=User.Role.CLIENT,
            **validated_data,
        )
        ClientProfile.objects.get_or_create(user=user)
        return user
