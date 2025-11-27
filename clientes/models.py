from django.utils import timezone
from django.db import models
from django.conf import settings

# Create your models here.

class Cliente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_cliente"
    )
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(default=timezone.now, blank=True, null=True)

    class Meta:
        ordering = ["-fecha_registro"]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        nombre = getattr(self.usuario, "username", None) or getattr(self.usuario, "email", "")
        return f"Cliente: {nombre}"