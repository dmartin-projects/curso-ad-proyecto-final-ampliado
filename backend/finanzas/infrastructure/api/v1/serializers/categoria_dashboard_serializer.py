# finanzas/infrastructure/api/v1/serializers/categoria_dashboard_serializer.py (módulos 77 y 87)
from rest_framework import serializers


class CategoriaDashboardSerializer(serializers.Serializer):
    categoria = serializers.IntegerField(allow_null=True)
    nombre = serializers.CharField()
    color = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    porcentaje = serializers.DecimalField(max_digits=5, decimal_places=1)
