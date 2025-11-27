from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Sobrescribimos el método para aceptar email o username
    def validate(self, attrs):
        username_or_email = attrs.get('username')
        password = attrs.get('password')

        # Intentar autenticar por email o username
        user = authenticate(username=username_or_email, password=password)

        if user is None:
            # Si no funcionó con username, intentamos con email
            from usuarios.models import Usuario
            try:
                usuario = Usuario.objects.get(email=username_or_email)
                user = authenticate(username=usuario.username, password=password)
            except Usuario.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError('Credenciales incorrectas.')

        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
            'rol': user.rol.nombre if user.rol else None,
        }

        update_last_login(None, user)
        return data
