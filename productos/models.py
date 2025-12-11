from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    # Costos y precios bases
    costo_base = models.DecimalField(max_digits=10, decimal_places=2)
    precio_cliente = models.DecimalField(max_digits=10, decimal_places=2)
    precio_distribuidor = models.DecimalField(max_digits=10, decimal_places=2)

    # Duración en días
    duracion_dias = models.PositiveIntegerField(default=30)

    # 🔥 ESTADO DEL PRODUCTO (re-agregado)
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el producto está disponible para usar en ventas."
    )

    # 🔥 NUEVOS CAMPOS PARA CUENTA COMPLETA
    es_cuenta_completa = models.BooleanField(
        default=False,
        help_text="Indica si este producto es una cuenta completa (ej: Netflix Completa)."
    )

    perfiles_cuenta = models.PositiveIntegerField(
        default=1,
        help_text="Número de perfiles que tiene este producto si es cuenta completa (ej: 5 para Netflix)."
    )

    # Fechas
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
