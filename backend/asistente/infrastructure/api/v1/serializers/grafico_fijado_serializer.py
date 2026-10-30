# asistente/infrastructure/api/v1/serializers/grafico_fijado_serializer.py (módulo 97)
from rest_framework import serializers

from asistente.application.chat.calculadora_de_graficos import EXTRACTORES
from asistente.domain.enums.tipo_grafico import TipoGrafico


class EspecificacionSerializer(serializers.Serializer):
    """QUÉ dibujar: lo que devuelve el chat en cada gráfico, tal cual (los números no: se recalculan)."""

    tipo = serializers.ChoiceField(choices=[t.value for t in TipoGrafico])
    titulo = serializers.CharField(max_length=80)
    fuente = serializers.ChoiceField(choices=sorted(EXTRACTORES))
    argumentos = serializers.DictField(required=False, default=dict)


class GraficoFijadoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    especificacion = EspecificacionSerializer()
    fijado_por = serializers.CharField(read_only=True, allow_null=True)
    grafico = serializers.JSONField(read_only=True, allow_null=True, help_text="etiquetas y series, calculadas ahora")
    error = serializers.CharField(read_only=True, allow_null=True)
