# finanzas/infrastructure/api/v1/serializers/mes_query_serializer.py (módulos 77 y 87)
from rest_framework import serializers


class MesQuerySerializer(serializers.Serializer):
    mes = serializers.DateField(input_formats=["%Y-%m"], required=False, help_text="AAAA-MM (por defecto, el actual)")
