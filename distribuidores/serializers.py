from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Distribuidor

Usuario = get_user_model()

class UsuarioBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ("id", "username", "email", "first_name", "last_name", "rol")


class DistribuidorSerializer(serializers.ModelSerializer):
    # Información completa del usuario (para mostrar)
    user_info = UsuarioBasicSerializer(source="user", read_only=True)

    # Para crear a través del admin (write-only)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=Usuario.objects.all(),
        write_only=True,
        required=False
    )

    # 🔥 NUEVO: user_id para lectura (lo que necesita el FRONTEND)
    user_id_read = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Distribuidor
        fields = (
            "id",
            "user",          # read-only (objeto user)
            "user_id",       # write-only
            "user_id_read",  # read-only → NECESARIO para el frontend
            "user_info",     # nested
            "empresa",
            "telefono",
            "activo",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def create(self, validated_data):
        """
        - Admin: puede crear para cualquier user (via user_id).
        - Vendedor: si no existe su distribuidor, se le crea para sí mismo.
        """
        request = self.context.get("request")
        user = validated_data.get("user")

        if request and request.user.is_authenticated:
            if request.user.rol == "admin":
                if not user:
                    raise serializers.ValidationError({"user_id": "Requerido para crear distribuidor."})
            else:
                # no admin: forzar a su propio usuario
                user = request.user

        # Evitar duplicados
        instance, created = Distribuidor.objects.get_or_create(user=user, defaults=validated_data)
        if not created:
            # Si ya existía → actualizar campos opcionales
            for k, v in validated_data.items():
                setattr(instance, k, v)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        # user es inmutable aquí
        validated_data.pop("user", None)
        validated_data.pop("user_id", None)
        return super().update(instance, validated_data)
