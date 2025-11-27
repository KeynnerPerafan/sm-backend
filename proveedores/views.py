from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Proveedor
from .serializers import ProveedorSerializer
from .permissions import IsAdmin

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all().order_by("-creado")
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
