# usuarios/infrastructure/api/v1/serializers/usuario_serializer.py (módulos 35 y 88)
from rest_framework import serializers

from usuarios.infrastructure.database.models.usuario_model import Usuario as UsuarioModel


class UsuarioSerializer(serializers.ModelSerializer):
    es_personal = serializers.BooleanField(source="is_staff", read_only=True)  # el frontend muestra "Soporte"

    class Meta:
        model = UsuarioModel
        fields = ["id", "email", "nombre", "apellidos", "fecha_alta", "es_personal"]
        read_only_fields = ["id", "email", "fecha_alta", "es_personal"]
