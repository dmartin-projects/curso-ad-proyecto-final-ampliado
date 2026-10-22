# finanzas/infrastructure/api/v1/serializers/recategorizar_serializer.py (módulos 87 y 88)
from rest_framework import serializers

from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel
from hogares.infrastructure.api.base.del_hogar_mixin import DelHogarMixin


class RecategorizarSerializer(DelHogarMixin, serializers.Serializer):
    campos_del_hogar = {"categoria": CategoriaModel}
    ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, max_length=1000)
    categoria = serializers.PrimaryKeyRelatedField(queryset=CategoriaModel.objects.none())
