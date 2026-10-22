# finanzas/infrastructure/api/v1/serializers/comercio_dashboard_serializer.py (módulos 77 y 87)
from rest_framework import serializers


class ComercioDashboardSerializer(serializers.Serializer):
    comercio = serializers.IntegerField()
    nombre = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    veces = serializers.IntegerField()
