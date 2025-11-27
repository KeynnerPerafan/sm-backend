from django.contrib import admin
from .models import Venta, VentaDetalle


class VentaDetalleInline(admin.TabularInline):
    model = VentaDetalle
    extra = 0
    fields = ("producto", "cantidad", "costo_unitario", "precio_unitario", "fecha_vencimiento")
    readonly_fields = ()
    show_change_link = True


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo_venta", "vendedor", "proveedor", "estado_pago", "es_garantia", "total_precio", "creado")
    list_filter = ("tipo_venta", "estado_pago", "es_garantia", "proveedor")
    search_fields = ("numero_pedido", "numero_pedido_proveedor", "comentario")
    inlines = [VentaDetalleInline]
    readonly_fields = ("numero_pedido", "total_costo", "total_precio", "creado", "actualizado")

    def save_model(self, request, obj, form, change):
        if not change and request.user and hasattr(request.user, "rol") and request.user.rol == "vendedor":
            obj.vendedor = request.user
        super().save_model(request, obj, form, change)
