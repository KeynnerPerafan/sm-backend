from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, buscar_productos

router = DefaultRouter()
router.register(r'', ProductoViewSet, basename='producto')

urlpatterns = [
    path("buscar/", buscar_productos),
]

urlpatterns = router.urls
