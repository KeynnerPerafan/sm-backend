from django.contrib import admin
from .models import Distribuidor

@admin.register(Distribuidor)
class DistribuidorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "empresa", "telefono", "activo", "created_at")
    list_filter = ("activo", "created_at")
    search_fields = ("user__username", "user__email", "empresa", "telefono")
    readonly_fields = ("created_at", "updated_at")
