# finanzas/infrastructure/api/v1/serializers/dia_dashboard_serializer.py (módulos 77 y 87)
from rest_framework import serializers


class DiaDashboardSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    gasto = serializers.DecimalField(max_digits=12, decimal_places=2)
    acumulado = serializers.DecimalField(max_digits=12, decimal_places=2)
