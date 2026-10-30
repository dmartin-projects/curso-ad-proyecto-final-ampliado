# asistente/infrastructure/api/v1/serializers/mensaje_serializer.py (módulo 97)
from rest_framework import serializers

ROLES = [("usuario", "usuario"), ("modelo", "modelo")]  # los visibles (los resultados de tools no se enseñan)


class MensajeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rol = serializers.ChoiceField(choices=ROLES)
    texto = serializers.CharField()
    datos = serializers.JSONField(help_text="gráficos, archivos (con su URL), propuestas (con su estado), seguimiento…")
    incompleto = serializers.BooleanField()
    nombre_adjunto = serializers.CharField()
    creado = serializers.DateTimeField()
