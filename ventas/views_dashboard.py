from django.utils.timezone import now
from django.db.models import Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Venta, VentaDetalle  # ajusta si tus modelos se llaman diferente

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_resumen(request):
    hoy = now().date()

    ventas_hoy = Venta.objects.filter(fecha_compra=hoy).count()

    # Ajusta este campo al que realmente usas como total en Venta
    ingresos_mes = Venta.objects.filter(
        fecha_compra__year=hoy.year,
        fecha_compra__month=hoy.month,
    ).aggregate(total=Sum("total_final"))["total"] or 0

    servicios_activos = VentaDetalle.objects.filter(
        fecha_vencimiento__gte=hoy
    ).count()

    return Response({
        "ventas_hoy": ventas_hoy,
        "ingresos_mes": ingresos_mes,
        "servicios_activos": servicios_activos,
    })
