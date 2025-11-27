# ventas/views.py
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q

from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Proveedor, Venta, VentaDetalle
from .serializers import ProveedorSerializer, VentaSerializer, VentaDetalleSerializer
from core.permissions import IsAdminOrVendor

from ventas.models import Venta
from clientes.models import Cliente
from productos.models import Producto
from distribuidores.models import Distribuidor
from proveedores.models import Proveedor

# ============================================
# PROVEEDORES
# ============================================
class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrVendor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "iniciales", "contacto", "telefono"]
    ordering = ["nombre"]


# ============================================
# VENTAS
# ============================================
class VentaViewSet(viewsets.ModelViewSet):
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrVendor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["numero_pedido", "numero_pedido_proveedor", "comentario"]
    ordering = ["-creado"]

    def get_queryset(self):
        qs = Venta.objects.select_related(
            "vendedor", "cliente", "distribuidor", "proveedor"
        ).prefetch_related("detalles", "detalles__producto")

        user = self.request.user
        if user.rol == "admin":
            return qs
        if user.rol == "vendedor":
            return qs.filter(vendedor=user)
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.rol == "vendedor":
            serializer.save(vendedor=user)
        else:
            serializer.save()

    @action(detail=True, methods=["post"], url_path="recalcular")
    def recalcular(self, request, pk=None):
        venta = self.get_object()
        venta.recalcular_totales(commit=True)
        return Response({
            "ok": True,
            "total_costo": str(venta.total_costo),
            "total_precio": str(venta.total_precio)
        })

    @action(detail=True, methods=["get"], url_path="credenciales")
    def credenciales(self, request, pk=None):
        venta = self.get_object()
        detalles = venta.detalles.all()

        lista = []
        for d in detalles:
            for cred in (d.credenciales or []):
                lista.append({
                    "producto": d.producto.nombre,
                    "email": cred.get("email"),
                    "password": cred.get("password"),
                    "nota": cred.get("nota"),
                    "cuenta_completa": cred.get("cuenta_completa", False),
                    "fecha_vencimiento": d.fecha_vencimiento,
                })

        return Response({
            "venta": venta.id,
            "cliente": venta.cliente.usuario.username if venta.cliente else None,
            "distribuidor": venta.distribuidor.user.username if venta.distribuidor else None,
            "credenciales": lista
        })


# ============================================
# DETALLES DE VENTA
# ============================================
class VentaDetalleViewSet(viewsets.ModelViewSet):
    serializer_class = VentaDetalleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrVendor]

    def get_queryset(self):
        qs = (
            Venta.objects.select_related(
                "vendedor", "cliente", "distribuidor", "proveedor"
            )
            .prefetch_related("detalles", "detalles__producto")
            .order_by("-creado")
        )

        user = self.request.user

        # ============================
        # PERMISOS
        # ============================
        if user.rol == "vendedor":
            qs = qs.filter(vendedor=user)

        # ============================
        # FILTROS PRO 🧠
        # ============================
        params = self.request.query_params

        # Tipo de venta
        if params.get("tipo_venta"):
            qs = qs.filter(tipo_venta=params["tipo_venta"])

        # Estado de pago
        if params.get("estado_pago"):
            qs = qs.filter(estado_pago=params["estado_pago"])

        # Medio de pago
        if params.get("medio_pago"):
            qs = qs.filter(medio_pago=params["medio_pago"])

        # Cliente
        if params.get("cliente"):
            qs = qs.filter(cliente__id=params["cliente"])

        # Distribuidor
        if params.get("distribuidor"):
            qs = qs.filter(distribuidor__id=params["distribuidor"])

        # Proveedor
        if params.get("proveedor"):
            qs = qs.filter(proveedor__id=params["proveedor"])

        # Gabi
        if params.get("gabi") == "true":
            qs = qs.filter(es_gabi=True)

        # Garantía
        if params.get("garantia") == "true":
            qs = qs.filter(es_garantia=True)

        # Fecha desde
        if params.get("fecha_desde"):
            qs = qs.filter(fecha_compra__gte=params["fecha_desde"])

        # Fecha hasta
        if params.get("fecha_hasta"):
            qs = qs.filter(fecha_compra__lte=params["fecha_hasta"])

        # Search mejorado
        search = params.get("search")
        if search:
            qs = qs.filter(
                Q(numero_pedido__icontains=search)
                | Q(numero_pedido_proveedor__icontains=search)
                | Q(comentario__icontains=search)
                | Q(cliente__usuario__username__icontains=search)
                | Q(distribuidor__user__username__icontains=search)
                | Q(proveedor__nombre__icontains=search)
            )

        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        venta_id = self.request.data.get("venta") or self.request.query_params.get("venta")
        if venta_id:
            try:
                ctx["venta"] = Venta.objects.get(pk=venta_id)
            except Venta.DoesNotExist:
                pass
        return ctx


# ============================================
# 🔥 DASHBOARD RESUMEN (NUEVO)
# ============================================
class DashboardResumenAPIView(APIView):
    """
    Endpoint completo para alimentar tu dashboard Tailwind UI Premium.
    """
    permission_classes = [IsAuthenticated, IsAdminOrVendor]

    def get(self, request, *args, **kwargs):

        from productos.models import Producto
        from clientes.models import Cliente
        from distribuidores.models import Distribuidor

        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)

        # Ventas de hoy
        ventas_hoy = Venta.objects.filter(fecha_compra=hoy)
        total_ventas_hoy = ventas_hoy.aggregate(total=Sum("total_final"))["total"] or 0
        cantidad_ventas_hoy = ventas_hoy.count()

        # Ventas del mes
        ventas_mes = Venta.objects.filter(fecha_compra__gte=inicio_mes, fecha_compra__lte=hoy)
        total_ventas_mes = ventas_mes.aggregate(total=Sum("total_final"))["total"] or 0
        cantidad_ventas_mes = ventas_mes.count()

        # Ticket promedio
        ticket_promedio = (
            total_ventas_mes / cantidad_ventas_mes if cantidad_ventas_mes > 0 else 0
        )

        # Ticket más alto del mes
        ticket_mas_alto = (
            ventas_mes.order_by("-total_final")
            .values_list("total_final", flat=True)
            .first()
            or 0
        )

        # Promedio ventas diario del mes
        dias_transcurridos = (hoy - inicio_mes).days + 1
        promedio_ventas_diario = (
            total_ventas_mes / dias_transcurridos if dias_transcurridos > 0 else 0
        )

        # Crecimiento día vs ayer
        ayer = hoy - timedelta(days=1)
        total_ayer = (
            Venta.objects.filter(fecha_compra=ayer).aggregate(total=Sum("total_final"))["total"]
            or 0
        )
        crecimiento_hoy_vs_ayer = (
            ((total_ventas_hoy - total_ayer) / total_ayer) * 100 if total_ayer > 0 else 0
        )

        # Crecimiento mes actual vs anterior
        mes_anterior_fin = inicio_mes - timedelta(days=1)
        mes_anterior_inicio = mes_anterior_fin.replace(day=1)
        ventas_mes_anterior = Venta.objects.filter(
            fecha_compra__gte=mes_anterior_inicio,
            fecha_compra__lte=mes_anterior_fin,
        )
        total_mes_anterior = (
            ventas_mes_anterior.aggregate(total=Sum("total_final"))["total"] or 0
        )
        crecimiento_mes_vs_anterior = (
            ((total_ventas_mes - total_mes_anterior) / total_mes_anterior) * 100
            if total_mes_anterior > 0
            else 0
        )

        # Serie de 7 días
        ventas_por_dia = []
        for i in range(6, -1, -1):
            fecha = hoy - timedelta(days=i)
            total = (
                Venta.objects.filter(fecha_compra=fecha).aggregate(total=Sum("total_final"))[
                    "total"
                ]
                or 0
            )
            ventas_por_dia.append({
                "fecha": fecha,
                "total": total,
            })

        # Últimas ventas
        ultimas_ventas_qs = (
            Venta.objects.select_related("cliente", "distribuidor")
            .order_by("-creado")[:5]
        )

        ultimas_ventas = []
        for v in ultimas_ventas_qs:
            ultimas_ventas.append({
                "id": v.id,
                "numero_pedido": v.numero_pedido,
                "cliente_nombre": getattr(v.cliente, "nombre", None),
                "distribuidor_nombre": getattr(v.distribuidor, "nombre", None),
                "total_final": v.total_final,
                "fecha_compra": v.fecha_compra,
                "estado_pago": v.estado_pago,
            })

        # Totales simples
        total_clientes = Cliente.objects.count()
        total_productos = Producto.objects.count()
        total_distribuidores = Distribuidor.objects.count()
        total_proveedores = Proveedor.objects.count()

        return Response({
            "total_ventas_hoy": total_ventas_hoy,
            "cantidad_ventas_hoy": cantidad_ventas_hoy,
            "total_ventas_mes": total_ventas_mes,
            "ticket_promedio": ticket_promedio,
            "promedio_ventas_diario": promedio_ventas_diario,
            "ticket_mas_alto": ticket_mas_alto,
            "crecimiento_hoy_vs_ayer_porcentaje": crecimiento_hoy_vs_ayer,
            "crecimiento_mes_vs_anterior_porcentaje": crecimiento_mes_vs_anterior,
            "total_clientes": total_clientes,
            "total_productos": total_productos,
            "total_distribuidores": total_distribuidores,
            "total_proveedores": total_proveedores,
            "ventas_por_dia": ventas_por_dia,
            "ultimas_ventas": ultimas_ventas,
        })


@api_view(["GET"])
def buscar_global(request):
    q = request.GET.get("q", "").strip()

    if not q:
        return Response({
            "productos": [],
            "clientes": [],
            "ventas": [],
            "proveedores": [],
            "distribuidores": []
        })

    return Response({
        "productos": list(Producto.objects.filter(nombre__icontains=q).values("id", "nombre")),
        "clientes": list(Cliente.objects.filter(nombre__icontains=q).values("id", "nombre")),
        "ventas": list(Venta.objects.filter(numero_pedido__icontains=q).values("id", "numero_pedido")),
        "proveedores": list(Proveedor.objects.filter(nombre__icontains=q).values("id", "nombre")),
        "distribuidores": list(Distribuidor.objects.filter(nombre__icontains=q).values("id", "nombre")),
    })