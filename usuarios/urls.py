from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, ProfileView, UsuarioViewSet, AdminRegisterView

router = DefaultRouter()
router.register(r'', UsuarioViewSet, basename='usuario')

urlpatterns = [
    # Auth
    path('auth/login/', LoginView.as_view(), name='login'),       # POST {login, password}
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),

    # Perfil
    path('profile/', ProfileView.as_view(), name='profile'),

    # Admin: crear usuario
    path('auth/admin/register/', AdminRegisterView.as_view(), name='admin_register'),

    # CRUD usuarios (solo admin)
    path('', include(router.urls)),
]
