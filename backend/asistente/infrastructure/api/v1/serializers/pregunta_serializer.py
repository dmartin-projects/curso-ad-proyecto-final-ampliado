# asistente/infrastructure/api/v1/serializers/pregunta_serializer.py (módulo 97)
from rest_framework import serializers

MAX_TEXTO = 2000  # una pregunta, no un documento: lo largo va como adjunto


class PreguntaSerializer(serializers.Serializer):
    texto = serializers.CharField(max_length=MAX_TEXTO, trim_whitespace=True)
    archivo = serializers.FileField(required=False, help_text="Una foto o un PDF: su texto (OCR) entra en la pregunta")
