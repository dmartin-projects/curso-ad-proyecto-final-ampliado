# finanzas/infrastructure/api/v1/serializers/dashboard_serializer.py — solo salida (módulos 77 y 87)
#
# Documenta la forma en OpenAPI y formatea Decimal y fechas. Lee atributos del DashboardOutputDTO del use case.
from rest_framework import serializers

from finanzas.infrastructure.api.v1.serializers.categoria_dashboard_serializer import CategoriaDashboardSerializer
from finanzas.infrastructure.api.v1.serializers.comercio_dashboard_serializer import ComercioDashboardSerializer
from finanzas.infrastructure.api.v1.serializers.dia_dashboard_serializer import DiaDashboardSerializer
from finanzas.infrastructure.api.v1.serializers.mes_dashboard_serializer import MesDashboardSerializer
from finanzas.infrastructure.api.v1.serializers.presupuesto_dashboard_serializer import (
    PresupuestoDashboardSerializer,
)


class DashboardSerializer(serializers.Serializer):
    mes = serializers.DateField(format="%Y-%m")
    gastos = serializers.DecimalField(max_digits=12, decimal_places=2)
    ingresos = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    num_movimientos = serializers.IntegerField()
    gastos_mes_anterior = serializers.DecimalField(max_digits=12, decimal_places=2)
    variacion = serializers.DecimalField(max_digits=7, decimal_places=1, allow_null=True)
    por_categoria = CategoriaDashboardSerializer(many=True)
    acumulado = DiaDashboardSerializer(many=True)
    evolucion = MesDashboardSerializer(many=True)
    top_comercios = ComercioDashboardSerializer(many=True)
    presupuestos = PresupuestoDashboardSerializer(many=True)
    pendientes_revision = serializers.IntegerField()
