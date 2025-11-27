from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .serializers import (
    LoginSerializer,
    UsuarioSerializer,
    AdminRegisterSerializer,
)

Usuario = get_user_model()


# ---------------------------------------
#  /api/auth/login/
# ---------------------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response(s.validated_data, status=status.HTTP_200_OK)


# ---------------------------------------
#  /api/profile/
# ---------------------------------------
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)


# ---------------------------------------
# CRUD Usuarios (solo para admin)
# ---------------------------------------
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by("id")
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdminUser]


# ---------------------------------------
#  /api/usuarios/auth/admin/register/
#  Crear usuarios desde el panel admin
# ---------------------------------------
class AdminRegisterView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        s = AdminRegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        # save() ya maneja fecha_registro correctamente
        user = s.save()

        return Response(
            {
                "detail": "Usuario creado correctamente.",
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "rol": user.rol,
                "fecha_registro": user.fecha_registro,
            },
            status=status.HTTP_201_CREATED,
        )
