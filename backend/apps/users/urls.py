from rest_framework.routers import DefaultRouter

from .views import ClientProfileViewSet, StaffProfileViewSet, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("client-profiles", ClientProfileViewSet)
router.register("staff-profiles", StaffProfileViewSet)

urlpatterns = router.urls

