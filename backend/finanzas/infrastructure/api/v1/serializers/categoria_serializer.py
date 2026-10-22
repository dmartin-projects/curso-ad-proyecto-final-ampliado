# finanzas/infrastructure/api/v1/serializers/categoria_serializer.py (módulos 33 y 87)
#
# Entrada: valida el FORMATO (tipos, obligatorios, que el id sea de tu hogar) y entrega los datos al use case con
# a_dominio(). Las REGLAS son del dominio: la jerarquía (dos niveles, sin ciclos) es Categoria.colgar_de() y el
# nombre repetido lo traduce el command repository desde la constraint. Salida: la forma de la response.
from rest_framework import serializers

from core.infrastructure.api.serializers.a_dominio_mixin import ADominioMixin
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel
from hogares.api.base import DelHogarMixin


class CategoriaSerializer(DelHogarMixin, ADominioMixin, serializers.ModelSerializer):
    campos_del_hogar = {"padre": CategoriaModel}
    relaciones = {"padre": "padre_id"}

    class Meta:
        model = CategoriaModel
        fields = ["id", "nombre", "padre", "color", "icono", "orden", "es_ingreso"]
