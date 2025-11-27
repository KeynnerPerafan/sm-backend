from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

Usuario = get_user_model()


# ============================
#   LOGIN
# ============================
class LoginSerializer(serializers.Serializer):
    # Acepta email o username en "login"
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")

        try:
            user = Usuario.objects.get(
                Q(username__iexact=login) | Q(email__iexact=login)
            )
        except Usuario.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "La combinación de credenciales no tiene una cuenta activa."
                    ]
                }
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["La cuenta está inactiva."]}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "La combinación de credenciales no tiene una cuenta activa."
                    ]
                }
            )

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return {
            "access": access,
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "rol": getattr(user, "rol", None),
            },
        }


# ============================
#   USUARIO (CRUD)
# ============================
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = (
            "id",
            "username",
            "email",
            "rol",
            "whatsapp",
            "telefono",
            "is_active",
            "is_staff",
            "fecha_registro",  # 👈 nuevo campo visible en responses
        )
        extra_kwargs = {
            "is_active": {"required": False},
            "is_staff": {"required": False},
        }


# ============================
#   REGISTRO DESDE ADMIN
# ============================
class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # Permitimos enviar opcionalmente la fecha de registro
    fecha_registro = serializers.DateField(required=False)

    class Meta:
        model = Usuario
        fields = (
            "username",
            "email",
            "password",
            "rol",
            "telefono",
            "whatsapp",
            "fecha_registro",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        rol = validated_data.get("rol", "cliente")
        fecha_registro = validated_data.pop("fecha_registro", None)

        # Creamos instancia de usuario
        user = Usuario(**validated_data)

        # Fecha de registro: si no la envían, usamos hoy
        user.fecha_registro = fecha_registro or timezone.now().date()

        # Seteamos contraseña
        user.set_password(password)

        # Reglas por rol
        if rol == "admin":
            user.is_staff = True
            user.is_superuser = True
        elif rol == "vendedor":
            # si quieres que el vendedor pueda entrar al admin de Django, pon True
            user.is_staff = False

        user.save()
        return user
