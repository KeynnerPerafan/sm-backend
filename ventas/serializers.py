from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from .models import Proveedor, Venta, VentaDetalle
from productos.models import Producto
from productos.serializers import ProductoSerializer



# =========================================================
#   PROVEEDOR
# =========================================================
class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ["id", "nombre", "iniciales", "contacto", "telefono"]


# =========================================================
#   LIST SERIALIZER PERSONALIZADO PARA DETALLES
# =========================================================
class VentaDetalleListSerializer(serializers.ListSerializer):
    """
    Asegura que el contexto (incluyendo venta) se pase a cada ítem.
    """
    def to_internal_value(self, data):
        # Propagamos contexto al child serializer
        self.child.context.update(self.context)
        return super().to_internal_value(data)


# =========================================================
#   DETALLE
# =========================================================
class VentaDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source="producto.nombre")
    producto_info = ProductoSerializer(read_only=True, source="producto")
    

    class Meta:
        model = VentaDetalle
        list_serializer_class = VentaDetalleListSerializer
        fields = [
            "id", "producto", "producto_nombre", "producto_info", "cantidad",
            "costo_unitario", "precio_unitario",
            "fecha_vencimiento", "credenciales", "comentario",
            "creado", "actualizado"
        ]
        read_only_fields = ["creado", "actualizado"]

    def validate(self, data):
        producto = data.get("producto")

        if not producto:
            raise serializers.ValidationError("Debes seleccionar un producto.")

        venta = self.context.get("venta", None)

        # Precio por defecto si no viene
        if venta and not data.get("precio_unitario"):
            data["precio_unitario"] = (
                producto.precio_distribuidor
                if venta.tipo_venta == "distribuidor"
                else producto.precio_cliente
            )

        # Costo por defecto si no viene
        if not data.get("costo_unitario"):
            data["costo_unitario"] = producto.costo_base

        # Fecha vencimiento automática
        if venta and not data.get("fecha_vencimiento"):
            base = venta.fecha_compra
        elif not data.get("fecha_vencimiento"):
            base = timezone.now().date()
        else:
            base = None

        if base is not None and not data.get("fecha_vencimiento"):
            data["fecha_vencimiento"] = base + timedelta(
                days=producto.duracion_dias or 30
            )

        return data


# =========================================================
#   VENTA
# =========================================================
class VentaSerializer(serializers.ModelSerializer):
    vendedor_nombre = serializers.ReadOnlyField(source="vendedor.username")
    cliente_nombre = serializers.ReadOnlyField(source="cliente.nombre", default=None)
    distribuidor_nombre = serializers.ReadOnlyField(source="distribuidor.nombre", default=None)
    proveedor_nombre = serializers.ReadOnlyField(source="proveedor.nombre")

    detalles = VentaDetalleSerializer(many=True)

    class Meta:
        model = Venta
        fields = [
            "id",
            "tipo_venta",
            "cliente", "cliente_nombre",
            "distribuidor", "distribuidor_nombre",
            "vendedor", "vendedor_nombre",
            "proveedor", "proveedor_nombre",
            "numero_pedido_proveedor", "numero_pedido",
            "fecha_compra",
            "estado_pago", "medio_pago", "es_garantia", "es_gabi",
            "comentario",
            "total_costo",
            "total_precio",
            "descuento_porcentaje",
            "descuento_valor",
            "total_final",
            "detalles",
            "creado", "actualizado",
        ]
        read_only_fields = [
            "numero_pedido",
            "total_costo",
            "total_precio",
            "total_final",
            "creado", "actualizado",
        ]

    def to_internal_value(self, data):
        # Pasamos contexto (request, etc.) al child serializer
        self.fields["detalles"].child.context.update(self.context)
        return super().to_internal_value(data)

    def validate(self, data):
        tipo = data.get("tipo_venta") or getattr(self.instance, "tipo_venta", None)
        cliente = data.get("cliente") or getattr(self.instance, "cliente", None)
        distribuidor = data.get("distribuidor") or getattr(self.instance, "distribuidor", None)
        proveedor = data.get("proveedor") or getattr(self.instance, "proveedor", None)

        if tipo == "cliente" and not cliente:
            raise serializers.ValidationError("Para ventas a cliente final debes seleccionar un Cliente.")
        if tipo == "distribuidor" and not distribuidor:
            raise serializers.ValidationError("Para ventas a distribuidor debes seleccionar un Distribuidor.")
        if not proveedor:
            raise serializers.ValidationError("El proveedor es obligatorio.")

        return data

    def create(self, validated_data):
        detalles_data = validated_data.pop("detalles", [])

        # Crear la venta primero
        venta = Venta.objects.create(**validated_data)

        # Crear cada detalle usando los datos YA validados
        for d in detalles_data:
            VentaDetalle.objects.create(venta=venta, **d)

        venta.recalcular_totales(commit=True)
        return venta

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop("detalles", None)

        # Actualizar campos simples de la venta
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # Si llegan detalles, reemplazarlos
        if detalles_data is not None:
            instance.detalles.all().delete()
            for d in detalles_data:
                VentaDetalle.objects.create(venta=instance, **d)

        instance.recalcular_totales(commit=True)
        return instance
