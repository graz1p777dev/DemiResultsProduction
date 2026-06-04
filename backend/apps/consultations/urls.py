from rest_framework.routers import DefaultRouter

from .views import ConsultationMessageViewSet, ConsultationViewSet

router = DefaultRouter()
router.register("consultations", ConsultationViewSet)
router.register("messages", ConsultationMessageViewSet)

urlpatterns = router.urls

