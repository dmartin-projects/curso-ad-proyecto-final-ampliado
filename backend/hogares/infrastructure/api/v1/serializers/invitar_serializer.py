# hogares/infrastructure/api/v1/serializers/invitar_serializer.py (módulos 71 y 88)
from rest_framework import serializers

from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel


class InvitarSerializer(serializers.Serializer):
    email = serializers.EmailField()
    rol = serializers.ChoiceField(choices=MembresiaModel.Rol.choices, default=MembresiaModel.Rol.MIEMBRO)
