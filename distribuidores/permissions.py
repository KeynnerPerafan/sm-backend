from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrOwner(BasePermission):
    """
    Admin: acceso total.
    Vendedor: solo su propio perfil (retrieve/update/partial_update).
    Otros roles: sin acceso salvo admin.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request.user, "rol", None) == "admin":
            return True
        # owner
        return obj.user_id == request.user.id

    def has_permission(self, request, view):
        # List y create solo admin; retrieve/update/destroy se evalúan por objeto
        if getattr(request.user, "rol", None) == "admin":
            return True
        if view.action in ("retrieve", "update", "partial_update"):
            return True
        # bloquear list/create/destroy a no-admin
        return False
