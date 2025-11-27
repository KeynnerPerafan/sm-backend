from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Cliente
from .serializers import ClienteSerializer
from .permissions import IsAdminOrSellerOrReadOwn

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.select_related("usuario").all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSellerOrReadOwn]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["usuario__username", "usuario__email", "telefono", "ciudad"]
    ordering_fields = ["fecha_registro", "ciudad", "activo"]
    ordering = ["-fecha_registro"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Admin/Vendedor ven todos; cliente ve solo su registro
        is_admin = user.is_staff or user.is_superuser
        is_seller = getattr(user, "rol", "").lower() == "vendedor" if hasattr(user, "rol") else False

        if is_admin or is_seller:
            return qs
        return qs.filter(usuario=user)
