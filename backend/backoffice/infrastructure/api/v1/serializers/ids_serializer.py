# backoffice/infrastructure/api/v1/serializers/ids_serializer.py (módulos 79 y 88)
from rest_framework import serializers


class IdsSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, max_length=500)
