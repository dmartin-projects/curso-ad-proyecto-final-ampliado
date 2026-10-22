# finanzas/infrastructure/api/v1/serializers/mes_dashboard_serializer.py (módulos 77 y 87)
from rest_framework import serializers


class MesDashboardSerializer(serializers.Serializer):
    mes = serializers.DateField(format="%Y-%m")
    gastos = serializers.DecimalField(max_digits=12, decimal_places=2)
    ingresos = serializers.DecimalField(max_digits=12, decimal_places=2)
