from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrSellerOrReadOwn(BasePermission):
    """
    - Admin/Vendedor: acceso total.
    - Cliente: puede leer/editar solo su propio perfil.
    Ajusta la detección de roles según tu modelo `Usuario`.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Si tu Usuario tiene enum/choices de rol:
        # role = getattr(user, "rol", None)
        # is_admin = str(role).lower() == "admin" or user.is_staff or user.is_superuser
        # is_seller = str(role).lower() == "vendedor"
        # Simplificado: staff/superuser son admin, ajusta si usas otro campo:
        is_admin = user.is_staff or user.is_superuser
        is_seller = getattr(user, "rol", "").lower() == "vendedor" if hasattr(user, "rol") else False

        if is_admin or is_seller:
            return True

        # Cliente: solo su propio objeto
        return obj.usuario_id == user.id

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return True
