from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "duracion_dias",
        "costo_base",
        "precio_cliente",
        "precio_distribuidor",
        "es_cuenta_completa",   # nuevo campo
        "perfiles_cuenta",      # nuevo campo
        "creado",
        "actualizado",
    )

    list_filter = (
        "es_cuenta_completa",   # filtrado útil
    )

    search_fields = ("nombre",)

    readonly_fields = ("creado", "actualizado")
