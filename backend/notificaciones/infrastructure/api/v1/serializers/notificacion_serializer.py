# notificaciones/infrastructure/api/v1/serializers/notificacion_serializer.py (módulos 76 y 88)
from rest_framework import serializers

from notificaciones.infrastructure.database.models.notificacion_model import Notificacion as NotificacionModel


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionModel
        fields = ["id", "tipo", "titulo", "mensaje", "enlace", "hogar", "datos", "leida", "creado"]
        read_only_fields = fields
