# informes/infrastructure/api/v1/serializers/informe_encolado_serializer.py (módulos 78 y 88)
from rest_framework import serializers


class InformeEncoladoSerializer(serializers.Serializer):
    mes = serializers.CharField()
    estado = serializers.CharField()
