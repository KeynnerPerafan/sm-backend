from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Producto
from .serializers import ProductoSerializer
from core.permissions import IsAdminOrVendor

class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrVendor]

    def get_queryset(self):
        """
        - Admin: ve todos los productos.
        - Distribuidor / Cliente: solo los activos.
        """
        user = self.request.user

        # 🔥 SIEMPRE construimos un queryset nuevo desde el manager
        qs = Producto.objects.all().order_by("-creado")   # o "-id" si prefieres

        if getattr(user, "rol", None) == "admin":
            return qs

        return qs.filter(activo=True)
