from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "duracion_dias", "costo_base", "precio_cliente", "precio_distribuidor", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    readonly_fields = ("creado", "actualizado")
