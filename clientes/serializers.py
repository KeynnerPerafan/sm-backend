from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    # Campos de solo lectura útiles para el frontend
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    usuario_email = serializers.EmailField(source="usuario.email", read_only=True)

    class Meta:
        model = Cliente
        fields = [
            "id", "usuario", "usuario_username", "usuario_email",
            "telefono", "direccion", "ciudad", "notas",
            "activo", "fecha_registro",
        ]
        read_only_fields = ["fecha_registro"]