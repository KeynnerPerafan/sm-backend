from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "telefono", "whatsapp", "activo")
    search_fields = ("nombre", "telefono", "whatsapp")
