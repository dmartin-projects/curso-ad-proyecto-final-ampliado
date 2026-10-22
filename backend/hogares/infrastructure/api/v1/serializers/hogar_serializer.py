# hogares/infrastructure/api/v1/serializers/hogar_serializer.py (módulos 71 y 88)
from rest_framework import serializers

from core.infrastructure.api.serializers.regla import regla
from hogares.domain.bo.hogar import comprobar_zona_horaria
from hogares.infrastructure.database.models.hogar_model import Hogar as HogarModel


class HogarSerializer(serializers.ModelSerializer):
    mi_rol = serializers.CharField(read_only=True)  # anotado en el queryset
    num_miembros = serializers.IntegerField(read_only=True)

    class Meta:
        model = HogarModel
        fields = ["id", "nombre", "moneda", "zona_horaria", "mi_rol", "num_miembros", "creado"]
        read_only_fields = ["creado"]

    # la regla es del dominio (Hogar); aquí solo se llama, para dar todos los errores del formulario a la vez
    def validate_zona_horaria(self, valor: str) -> str:
        return regla(comprobar_zona_horaria, valor)
