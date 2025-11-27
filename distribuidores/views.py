from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Distribuidor
from .serializers import DistribuidorSerializer
from .permissions import IsAdminOrOwner

class DistribuidorViewSet(viewsets.ModelViewSet):
    serializer_class = DistribuidorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        # 🔥 siempre un queryset nuevo desde el manager
        qs = Distribuidor.objects.select_related("user").all()
        user = self.request.user

        if getattr(user, "rol", None) == "admin":
            return qs

        # vendedores / otros: solo su propio registro
        return qs.filter(user=user)
