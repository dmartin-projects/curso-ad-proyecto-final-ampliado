# finanzas/infrastructure/api/v1/serializers/presupuesto_dashboard_serializer.py (módulos 77 y 87)
from rest_framework import serializers


class PresupuestoDashboardSerializer(serializers.Serializer):
    categoria = serializers.CharField()
    importe = serializers.DecimalField(max_digits=10, decimal_places=2)
    gastado = serializers.DecimalField(max_digits=12, decimal_places=2)
    porcentaje = serializers.IntegerField()
