# asistente/infrastructure/api/v1/serializers/conversacion_serializer.py (módulo 97)
from rest_framework import serializers


class ConversacionSerializer(serializers.Serializer):
    """Lee un ConversacionOutputDTO; al crear, la carpeta (opcional); al modificar, el título o la carpeta."""

    id = serializers.IntegerField(read_only=True)
    titulo = serializers.CharField(max_length=80, required=False)
    carpeta = serializers.IntegerField(source="carpeta_id", allow_null=True, required=False)
    actualizada = serializers.DateTimeField(read_only=True, allow_null=True)

    def a_dominio(self) -> dict:
        """Solo lo que ha llegado: en un PATCH, lo que no se manda no se cambia."""
        return dict(self.validated_data)
