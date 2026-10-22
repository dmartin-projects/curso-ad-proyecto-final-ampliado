# backoffice/infrastructure/api/v1/serializers/resumen_serializer.py (módulos 79 y 88)
from rest_framework import serializers

from backoffice.infrastructure.api.v1.serializers.por_estado_serializer import PorEstadoSerializer


class ResumenSerializer(serializers.Serializer):
    tickets_24h = PorEstadoSerializer(many=True)
    tickets_atascados = serializers.IntegerField()
    importaciones_en_curso = serializers.IntegerField()
    importaciones_con_error_7d = serializers.IntegerField()
    hogares = serializers.IntegerField()
    usuarios_activos = serializers.IntegerField()
