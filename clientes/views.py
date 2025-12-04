from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Cliente
from .serializers import ClienteSerializer
from .permissions import IsAdminOrSellerOrReadOwn

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('-id')
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSellerOrReadOwn]

    # 🔍 Búsqueda + Ordenamiento (lo necesario)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["usuario__username", "usuario__email", "telefono", "ciudad"]
    ordering_fields = ["fecha_registro", "ciudad", "activo"]
    ordering = ["-fecha_registro"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Admin / Superuser = ve TODO
        if user.is_staff or user.is_superuser:
            return qs

        # Vendedor = ve TODO (si tu sistema maneja "rol")
        rol = getattr(user, "rol", "").lower()
        if rol == "vendedor":
            return qs

        # Cliente = solo ve su propio registro
        return qs.filter(usuario=user)
