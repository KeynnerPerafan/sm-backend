from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = "__all__"
        read_only_fields = ("id", "creado", "actualizado")

    def validate(self, data):
        """
        Evita que el precio cliente/distribuidor sea menor que el costo base.
        """
        costo = data.get("costo_base", getattr(self.instance, "costo_base", None))
        precio_cliente = data.get("precio_cliente", getattr(self.instance, "precio_cliente", None))
        precio_distribuidor = data.get("precio_distribuidor", getattr(self.instance, "precio_distribuidor", None))

        if precio_cliente and costo and precio_cliente < costo:
            raise serializers.ValidationError("El precio al cliente no puede ser menor que el costo base.")
        if precio_distribuidor and costo and precio_distribuidor < costo:
            raise serializers.ValidationError("El precio al distribuidor no puede ser menor que el costo base.")
        return data
