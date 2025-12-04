from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Producto
from .serializers import ProductoSerializer
from core.permissions import IsAdminOrVendor   # Ajusta si tu proyecto usa otro


class ProductoViewSet(viewsets.ModelViewSet):
    """
    - Admin: ve todos los productos
    - Distribuidor / Cliente: solo los activos
    - Búsqueda real
    - Ordenamiento
    - Paginación automática
    """
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrVendor]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "descripcion", "iniciales"]
    ordering_fields = [
        "creado",
        "nombre",
        "costo_base",
        "precio_cliente",
        "precio_distribuidor",
        "duracion_dias",
        "activo",
    ]
    ordering = ["-creado"]

    def get_queryset(self):
        user = self.request.user

        # 🔥 Siempre construir un queryset nuevo desde el manager
        qs = Producto.objects.all().order_by("-creado")

        # Admin ve todo
        if getattr(user, "rol", "").lower() == "admin":
            return qs

        # Distribuidor / cliente solo ven activos
        return qs.filter(activo=True)


# ============================================================
#   🔍 ENDPOINT OPCIONAL PARA BUSCADOR RÁPIDO (AUTOCOMPLETE)
# ============================================================
@api_view(["GET"])
def buscar_productos(request):
    q = request.GET.get("q", "").strip()

    productos = Producto.objects.filter(nombre__icontains=q)[:20]

    # 🔥 Debe usarse Response, no response(...)
    return Response(ProductoSerializer(productos, many=True).data)
