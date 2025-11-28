from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Proveedor
from .serializers import ProveedorSerializer
from .permissions import IsAdmin

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all().order_by("-creado")
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

@api_view(["GET"])
def buscar_proveedores(request):
    q = request.GET.get("q", "").strip()

    proveedores = Proveedor.objects.filter(nombre__icontains=q)[:15]
    return Response(ProveedorSerializer(proveedores, many=True).data)