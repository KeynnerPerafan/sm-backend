# ventas/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    ProveedorViewSet,
    VentaViewSet,
    VentaDetalleViewSet,
    DashboardResumenAPIView,
    buscar_global,  # 👈 AÑADIDO
)

from .views_dashboard import dashboard_resumen

router = DefaultRouter()
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'', VentaViewSet, basename='venta')
router.register(r'venta-detalles', VentaDetalleViewSet, basename='ventadetalle')

urlpatterns = [
    path("dashboard-resumen/", DashboardResumenAPIView.as_view(), name="dashboard-resumen"),
    path("buscar/", buscar_global, name="buscar_global"),
    path("dashboard-resumen/", dashboard_resumen, name="dashboard-resumen"),
]

urlpatterns += router.urls
