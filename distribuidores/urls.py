from rest_framework.routers import DefaultRouter
from .views import DistribuidorViewSet

router = DefaultRouter()
router.register(r"", DistribuidorViewSet, basename="distribuidor")

urlpatterns = router.urls
