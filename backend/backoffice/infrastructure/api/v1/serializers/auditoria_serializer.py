# backoffice/infrastructure/api/v1/serializers/auditoria_serializer.py (módulos 79 y 88)
from rest_framework import serializers

from core.models import RegistroAuditoria as RegistroAuditoriaModel


class AuditoriaSerializer(serializers.ModelSerializer):
    usuario = serializers.EmailField(source="usuario.email", read_only=True, default=None, allow_null=True)
    modelo = serializers.SerializerMethodField()

    class Meta:
        model = RegistroAuditoriaModel
        fields = ["id", "fecha", "usuario", "accion", "modelo", "object_id", "representacion", "cambios"]
        read_only_fields = fields

    def get_modelo(self, registro) -> str:
        return f"{registro.content_type.app_label}.{registro.content_type.model}"
