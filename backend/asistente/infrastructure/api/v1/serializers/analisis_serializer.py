# asistente/infrastructure/api/v1/serializers/analisis_serializer.py (módulo 105)
from rest_framework import serializers


class PedirAnalisisSerializer(serializers.Serializer):
    tarea = serializers.UUIDField(help_text="Un UUID que genera el cliente: con él llegan los avisos de progreso.")
    mes = serializers.RegexField(r"^\d{4}-\d{2}$", required=False, help_text="AAAA-MM; sin él, el mes en curso.")


class AnalisisPedidoSerializer(serializers.Serializer):
    tarea = serializers.UUIDField()
    mes = serializers.CharField()
