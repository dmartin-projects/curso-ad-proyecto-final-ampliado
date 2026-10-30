# asistente/infrastructure/api/v1/serializers/conversacion_detalle_serializer.py (módulo 97)
from rest_framework import serializers

from asistente.infrastructure.api.v1.serializers.conversacion_serializer import ConversacionSerializer
from asistente.infrastructure.api.v1.serializers.mensaje_serializer import MensajeSerializer


class ConversacionDetalleSerializer(serializers.Serializer):
    conversacion = ConversacionSerializer()
    mensajes = MensajeSerializer(many=True)
