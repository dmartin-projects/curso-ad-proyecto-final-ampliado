# hogares/infrastructure/api/v1/serializers/invitacion_serializer.py (módulos 71 y 88)
from rest_framework import serializers

from hogares.infrastructure.database.models.invitacion_model import Invitacion as InvitacionModel


class InvitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitacionModel
        fields = ["id", "email", "rol", "caduca", "aceptada"]
