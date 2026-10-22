# usuarios/infrastructure/api/v1/serializers/registro_serializer.py (módulos 35 y 88)
from django.contrib.auth import get_user_model
from rest_framework import serializers

Usuario = get_user_model()


class RegistroSerializer(serializers.Serializer):
    """Solo datos que no son secretos: la contraseña se elige al completar el registro."""

    email = serializers.EmailField(max_length=254)
    nombre = serializers.CharField(max_length=150, required=False, allow_blank=True)
    apellidos = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, email):
        # Sin comprobar si ya existe: la respuesta es la misma para un email nuevo o registrado. Un ModelSerializer
        # añadiría el UniqueValidator del campo, y su 400 "ya existe" diría qué emails tienen cuenta.
        return Usuario.objects.normalize_email(email).lower()
