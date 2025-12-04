from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Distribuidor
from .serializers import DistribuidorSerializer
from .permissions import IsAdminOrOwner

class DistribuidorViewSet(viewsets.ModelViewSet):
    serializer_class = DistribuidorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    # 🔍 Búsqueda y ordenamiento (opcional pero recomendado)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "user__username",
        "user__email",
        "empresa",
        "telefono",
    ]
    ordering_fields = ["id", "empresa", "telefono", "activo"]
    ordering = ["-id"]

    def get_queryset(self):
        # Usamos select_related para optimizar
        qs = Distribuidor.objects.select_related("user").all()
        user = self.request.user

        # 🔥 Admin ve todo
        if getattr(user, "rol", "").lower() == "admin" or user.is_superuser:
            return qs

        # 🔥 Distribuidor / Vendedor: solo su propio registro
        return qs.filter(user=user)
