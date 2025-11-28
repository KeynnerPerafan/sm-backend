from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProveedorViewSet, buscar_proveedores

router = DefaultRouter()
router.register(r'', ProveedorViewSet, basename="proveedores")

urlpatterns = [
    path("buscar/", buscar_proveedores),

]

urlpatterns = router.urls
