from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    duracion_dias = models.PositiveIntegerField(default=30)
    costo_base = models.DecimalField(max_digits=10, decimal_places=2)
    precio_cliente = models.DecimalField(max_digits=10, decimal_places=2)
    precio_distribuidor = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-creado"]

    def __str__(self):
        return self.nombre
