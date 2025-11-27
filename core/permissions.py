from rest_framework.permissions import BasePermission

class IsAdminOrVendor(BasePermission):
    """
    Admin: acceso total.
    Vendedor: solo ventas propias.
    Cliente: sin acceso.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.rol == "admin":
            return True

        if request.user.rol == "vendedor":
            return True  # luego filtramos en get_queryset()

        return False  # cliente no accede

    def has_object_permission(self, request, view, obj):
        if request.user.rol == "admin":
            return True

        if request.user.rol == "vendedor":
            return obj.vendedor_id == request.user.id

        return False

