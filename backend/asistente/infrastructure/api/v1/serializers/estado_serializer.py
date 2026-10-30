# asistente/infrastructure/api/v1/serializers/estado_serializer.py (módulo 107)
from rest_framework import serializers

from asistente.domain.exceptions.asistente_no_disponible_exception import AsistenteNoDisponibleException


class EstadoDelAsistenteSerializer(serializers.Serializer):
    activo = serializers.BooleanField()
    motivo = serializers.ChoiceField(choices=["", "apagado", "sin_modelos"])
    mensaje = serializers.SerializerMethodField(help_text="Para enseñarlo tal cual si no está activo")

    def get_mensaje(self, estado) -> str:
        return "" if estado.activo else AsistenteNoDisponibleException(estado.motivo).mensaje
