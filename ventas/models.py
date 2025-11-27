from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal

from usuarios.models import Usuario
from clientes.models import Cliente
from distribuidores.models import Distribuidor
from productos.models import Producto
from datetime import timedelta
from proveedores.models import Proveedor

class Venta(models.Model):
    TIPO_VENTA_CHOICES = [
        ("cliente", "Cliente final"),
        ("distribuidor", "Distribuidor"),
    ]

    ESTADO_PAGO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("pagado", "Pagado"),
        ("garantia", "Garantía"),
    ]

    MEDIO_PAGO_CHOICES = [
        ("nequi", "Nequi"),
        ("efectivo", "Efectivo"),
        ("transferencia", "Transferencia"),
        ("otro", "Otro"),
    ]

    tipo_venta = models.CharField(
        max_length=20,
        choices=TIPO_VENTA_CHOICES,
        default="cliente"
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="ventas"
    )
    distribuidor = models.ForeignKey(
        Distribuidor,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="ventas"
    )

    vendedor = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="ventas"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='ventas'
    )

    numero_pedido_proveedor = models.CharField(
        max_length=50,
        help_text="Número de pedido que te da el proveedor"
    )
    numero_pedido = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        editable=False
    )

    fecha_compra = models.DateField(default=timezone.now)

    estado_pago = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO_CHOICES,
        default="pendiente"
    )
    medio_pago = models.CharField(
        max_length=20,
        choices=MEDIO_PAGO_CHOICES,
        default="nequi"
    )
    es_garantia = models.BooleanField(default=False)
    es_gabi = models.BooleanField(default=False)

    comentario = models.TextField(blank=True, null=True)

    total_costo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_precio = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    # DESCUENTOS
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descuento_valor = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_final = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-creado"]

    # -----------------------------
    # VALIDACIÓN
    # -----------------------------
    def clean(self):
        if self.tipo_venta == "cliente" and not self.cliente:
            raise ValidationError("Para ventas a cliente final debes seleccionar un Cliente.")

        if self.tipo_venta == "distribuidor" and not self.distribuidor:
            raise ValidationError("Para ventas a distribuidor debes seleccionar un Distribuidor.")

        if not self.proveedor:
            raise ValidationError("El proveedor es obligatorio.")

    # -----------------------------
    # SAVE OVERRIDE
    # -----------------------------
    def save(self, *args, **kwargs):
        # primero guardamos para tener ID
        super().save(*args, **kwargs)

        # Recalcular totales (costo, precio, total_final)
        self.recalcular_totales(commit=True)

        # Generar numero_pedido si no existe
        if not self.numero_pedido and self.proveedor and self.id:
            pref = (self.proveedor.iniciales or "").upper()
            self.numero_pedido = f"{pref}-{self.numero_pedido_proveedor}-{self.id}"
            super().save(update_fields=["numero_pedido"])

    # -----------------------------
    # CALCULO DE TOTALES (CORREGIDO)
    # -----------------------------
    def recalcular_totales(self, commit=False):
        agregados = self.detalles.aggregate(
            total_costo=Coalesce(
                Sum(
                    F("costo_unitario") * F("cantidad"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
            ),
            total_precio=Coalesce(
                Sum(
                    F("precio_unitario") * F("cantidad"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
            ),
        )

        self.total_costo = agregados["total_costo"]
        self.total_precio = agregados["total_precio"]

        # Aplicación de descuentos
        total_final = self.total_precio

        if self.descuento_porcentaje and self.descuento_porcentaje > 0:
            total_final -= total_final * (self.descuento_porcentaje / Decimal("100"))

        if self.descuento_valor and self.descuento_valor > 0:
            total_final -= self.descuento_valor

        if total_final < 0:
            total_final = Decimal("0.00")

        self.total_final = total_final

        if commit:
            super().save(
                update_fields=["total_costo", "total_precio", "total_final"]
            )

    def __str__(self):
        return f"Venta #{self.id or 'NUEVA'} - {self.get_tipo_venta_display()}"


class VentaDetalle(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)

    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    fecha_vencimiento = models.DateField()

    credenciales = models.JSONField(default=list, blank=True)

    comentario = models.TextField(blank=True, null=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def clean(self):
        if self.cantidad < 1:
            raise ValidationError("La cantidad debe ser al menos 1.")

    def _precio_por_tipo(self, venta: Venta):
        return (
            self.producto.precio_distribuidor
            if venta.tipo_venta == "distribuidor"
            else self.producto.precio_cliente
        )

    def _costo_por_defecto(self):
        return self.producto.costo_base

    def _fecha_venc_defecto(self, venta: Venta):
        base = venta.fecha_compra or timezone.now().date()
        return base + timedelta(days=self.producto.duracion_dias or 30)

    def save(self, *args, **kwargs):
        creating = self.pk is None

        if creating:
            if not self.costo_unitario:
                self.costo_unitario = self._costo_por_defecto()

            if not self.precio_unitario:
                self.precio_unitario = self._precio_por_tipo(self.venta)

            if not self.fecha_vencimiento:
                self.fecha_vencimiento = self._fecha_venc_defecto(self.venta)

        super().save(*args, **kwargs)

        # Recalcular totals de la venta
        self.venta.recalcular_totales(commit=True)

    def __str__(self):
        return f"Detalle #{self.id or 'NUEVO'} - {self.producto.nombre}"
