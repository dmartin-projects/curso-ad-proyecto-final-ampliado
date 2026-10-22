# tickets/infrastructure/api/v1/serializers/url_archivo_serializer.py (módulos 74 y 88)
from rest_framework import serializers


class UrlArchivoSerializer(serializers.Serializer):
    url = serializers.URLField()
