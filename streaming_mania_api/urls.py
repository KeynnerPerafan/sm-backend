from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from usuarios.views import LoginView, ProfileView  # 👈 usamos tu LoginView nuevo

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # 🔐 JWT Auth personalizado
    path('api/auth/login/', LoginView.as_view(), name='login'),  # ✅ usa login/email
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # 👤 Perfil del usuario autenticado
    path('api/profile/', ProfileView.as_view(), name='profile'),

    # 🌐 Rutas por app
    path('api/usuarios/', include('usuarios.urls')),
    path('api/clientes/', include('clientes.urls')),
    path('api/distribuidores/', include('distribuidores.urls')),
    path('api/proveedores/', include('proveedores.urls')),
    path('api/productos/', include('productos.urls')),
    path('api/ventas/', include('ventas.urls')),
]
