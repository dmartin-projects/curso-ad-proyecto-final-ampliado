# backoffice/infrastructure/api/v1/serializers/hogar_detalle_soporte_serializer.py (módulos 79 y 88)

from backoffice.infrastructure.api.v1.serializers.hogar_soporte_serializer import HogarSoporteSerializer
from backoffice.infrastructure.api.v1.serializers.miembro_soporte_serializer import MiembroSoporteSerializer


class HogarDetalleSoporteSerializer(HogarSoporteSerializer):
    miembros = MiembroSoporteSerializer(source="membresias", many=True, read_only=True)

    class Meta(HogarSoporteSerializer.Meta):
        fields = [*HogarSoporteSerializer.Meta.fields, "miembros"]
        read_only_fields = fields
