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
#   LISTADO LIGERO PARA TABLAS (React + Flutter)
# =========================================================
class VentaListSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField()
    distribuidor_nombre = serializers.SerializerMethodField()
    vendedor_nombre = serializers.ReadOnlyField(source="vendedor.username")
    proveedor_nombre = serializers.ReadOnlyField(source="proveedor.nombre")

    cliente_info = serializers.SerializerMethodField()
    distribuidor_info = serializers.SerializerMethodField()
    proveedor_info = serializers.SerializerMethodField()

    # 🔥 NUEVO: indica si alguna credencial es renovable
    tiene_renovables = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = [
            "id",
            "numero_pedido",
            "numero_pedido_proveedor",

            "tipo_venta",

            "cliente",
            "cliente_nombre",
            "cliente_info",

            "distribuidor",
            "distribuidor_nombre",
            "distribuidor_info",

            "proveedor",
            "proveedor_nombre",
            "proveedor_info",

            "vendedor_nombre",

            "fecha_compra",
            "estado_pago",
            "medio_pago",

            "es_garantia",
            "es_gabi",

            "tiene_renovables",   # 🔥 añadido al listado

            "total_final",
        ]

    # =========================================================
    #   CAMPOS CALCULADOS
    # =========================================================

    def get_cliente_nombre(self, obj):
        if obj.cliente:
            return obj.cliente.usuario.username
        return None

    def get_distribuidor_nombre(self, obj):
        if obj.distribuidor:
            return obj.distribuidor.user.username
        return None

    def get_cliente_info(self, obj):
        c = obj.cliente
        if not c:
            return None
        return {
            "id": c.id,
            "usuario_username": c.usuario.username,
            "usuario_email": c.usuario.email,
        }

    def get_distribuidor_info(self, obj):
        d = obj.distribuidor
        if not d:
            return None
        return {
            "id": d.id,
            "username": d.user.username,
            "email": d.user.email,
        }

    def get_proveedor_info(self, obj):
        p = obj.proveedor
        if not p:
            return None
        return {
            "id": p.id,
            "nombre": p.nombre,
            "iniciales": p.iniciales,
        }

    # =========================================================
    #   🔥 NUEVO: DETECTAR SI HAY CREDENCIALES RENOVABLES
    # =========================================================
    def get_tiene_renovables(self, obj):
        """
        Devuelve True si ALGUNA credencial en ALGÚN detalle
        tiene renovable=True
        """
        for d in obj.detalles.all():
            for cred in (d.credenciales or []):
                if cred.get("renovable") is True:
                    return True
        return False


# =========================================================
#   DETALLE SERIALIZER
# =========================================================
class VentaDetalleListSerializer(serializers.ListSerializer):
    def to_internal_value(self, data):
        self.child.context.update(self.context)
        return super().to_internal_value(data)


class VentaDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source="producto.nombre")
    producto_info = ProductoSerializer(read_only=True, source="producto")

    class Meta:
        model = VentaDetalle
        list_serializer_class = VentaDetalleListSerializer
        fields = [
            "id",
            "producto",
            "producto_nombre",
            "producto_info",

            "cantidad",
            "costo_unitario",
            "precio_unitario",

            "fecha_vencimiento",
            "credenciales",   # renovable vive aquí
            "comentario",

            "creado",
            "actualizado",
        ]
        read_only_fields = ["creado", "actualizado"]

    def validate(self, data):
        producto = data.get("producto")

        if not producto:
            raise serializers.ValidationError("Debes seleccionar un producto.")

        venta = self.context.get("venta", None)

        # Precio por tipo
        if venta and not data.get("precio_unitario"):
            data["precio_unitario"] = (
                producto.precio_distribuidor
                if venta.tipo_venta == "distribuidor"
                else producto.precio_cliente
            )

        # Costo base
        if not data.get("costo_unitario"):
            data["costo_unitario"] = producto.costo_base

        # Fecha vencimiento
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

        # =========================================================
        #   🔥 ASEGURAR QUE "renovable" EXISTA EN TODAS LAS CREDENCIALES
        # =========================================================
        credenciales = data.get("credenciales", [])

        for cred in credenciales:
            if "renovable" not in cred:
                cred["renovable"] = False

        data["credenciales"] = credenciales

        return data


# =========================================================
#   SERIALIZER COMPLETO (CREAR / EDITAR)
# =========================================================
class VentaSerializer(serializers.ModelSerializer):
    vendedor_nombre = serializers.ReadOnlyField(source="vendedor.username")

    cliente_nombre = serializers.SerializerMethodField()
    distribuidor_nombre = serializers.SerializerMethodField()
    proveedor_nombre = serializers.ReadOnlyField(source="proveedor.nombre")

    cliente_info = serializers.SerializerMethodField()
    distribuidor_info = serializers.SerializerMethodField()
    proveedor_info = serializers.SerializerMethodField()

    detalles = VentaDetalleSerializer(many=True)

    class Meta:
        model = Venta
        fields = [
            "id",
            "tipo_venta",

            "cliente",
            "cliente_nombre",
            "cliente_info",

            "distribuidor",
            "distribuidor_nombre",
            "distribuidor_info",

            "vendedor",
            "vendedor_nombre",

            "proveedor",
            "proveedor_nombre",
            "proveedor_info",

            "numero_pedido_proveedor",
            "numero_pedido",
            "fecha_compra",

            "estado_pago",
            "medio_pago",
            "es_garantia",
            "es_gabi",
            "comentario",

            "total_costo",
            "total_precio",
            "descuento_porcentaje",
            "descuento_valor",
            "total_final",

            "detalles",
            "creado",
            "actualizado",
        ]
        read_only_fields = [
            "numero_pedido",
            "total_costo",
            "total_precio",
            "total_final",
            "creado",
            "actualizado",
        ]

    # ============================ CAMPOS CALCULADOS ============================

    def get_cliente_nombre(self, obj):
        if obj.cliente:
            return obj.cliente.usuario.username
        return None

    def get_distribuidor_nombre(self, obj):
        if obj.distribuidor:
            return obj.distribuidor.user.username
        return None

    def get_cliente_info(self, obj):
        c = obj.cliente
        if not c:
            return None
        return {
            "id": c.id,
            "usuario_username": c.usuario.username,
            "usuario_email": c.usuario.email,
            "telefono": c.telefono,
        }

    def get_distribuidor_info(self, obj):
        d = obj.distribuidor
        if not d:
            return None
        return {
            "id": d.id,
            "username": d.user.username,
            "email": d.user.email,
            "empresa": d.empresa,
            "telefono": d.telefono,
        }

    def get_proveedor_info(self, obj):
        p = obj.proveedor
        if not p:
            return None
        return {
            "id": p.id,
            "nombre": p.nombre,
            "iniciales": p.iniciales,
        }

    # ============================ CREAR / EDITAR ============================

    def to_internal_value(self, data):
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
        venta = Venta.objects.create(**validated_data)

        for d in detalles_data:
            VentaDetalle.objects.create(venta=venta, **d)

        venta.recalcular_totales(commit=True)
        return venta

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop("detalles", None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if detalles_data is not None:
            instance.detalles.all().delete()
            for d in detalles_data:
                VentaDetalle.objects.create(venta=instance, **d)

        instance.recalcular_totales(commit=True)
        return instance
