from django.db import models
from django.conf import settings

class Distribuidor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='distribuidor'
    )
    empresa = models.CharField(max_length=150, blank=True)      # opcional
    telefono = models.CharField(max_length=30, blank=True)      # opcional
    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Distribuidor'
        verbose_name_plural = 'Distribuidores'

    def __str__(self):
        return f"{self.user.username} (Distribuidor)"
