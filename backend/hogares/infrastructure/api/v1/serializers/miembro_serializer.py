# hogares/infrastructure/api/v1/serializers/miembro_serializer.py (módulos 71 y 88)
from rest_framework import serializers

from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel


class MiembroSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="usuario.email", read_only=True)
    nombre = serializers.CharField(source="usuario.get_full_name", read_only=True)

    class Meta:
        model = MembresiaModel
        fields = ["id", "email", "nombre", "rol", "creado"]
        read_only_fields = ["creado"]
