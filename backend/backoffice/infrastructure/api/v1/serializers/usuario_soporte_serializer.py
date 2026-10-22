# backoffice/infrastructure/api/v1/serializers/usuario_soporte_serializer.py (módulos 79 y 88)
from django.contrib.auth import get_user_model
from rest_framework import serializers


class UsuarioSoporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "nombre", "apellidos", "is_active", "is_staff", "fecha_alta", "last_login"]
        read_only_fields = ["id", "email", "nombre", "apellidos", "is_staff", "fecha_alta", "last_login"]
