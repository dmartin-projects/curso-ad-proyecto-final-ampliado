# usuarios/infrastructure/api/v1/serializers/cambiar_password_serializer.py (módulos 35 y 88)
from django.contrib.auth import password_validation
from rest_framework import serializers


class CambiarPasswordSerializer(serializers.Serializer):
    actual = serializers.CharField(write_only=True)
    nueva = serializers.CharField(write_only=True)

    def validate_actual(self, valor):
        if not self.context["request"].user.check_password(valor):
            raise serializers.ValidationError("La contraseña actual no es correcta.")
        return valor

    def validate_nueva(self, valor):
        password_validation.validate_password(valor, user=self.context["request"].user)
        return valor
