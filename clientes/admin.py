from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "telefono", "ciudad", "activo", "fecha_registro")
    list_filter = ("activo", "ciudad",)
    search_fields = ("usuario__username", "usuario__email", "telefono", "ciudad")
    readonly_fields = ("fecha_registro",)