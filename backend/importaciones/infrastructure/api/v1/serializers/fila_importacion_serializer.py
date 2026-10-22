# importaciones/infrastructure/api/v1/serializers/fila_importacion_serializer.py (módulos 75 y 88)
from rest_framework import serializers

from importaciones.infrastructure.database.models.fila_importacion_model import FilaImportacion as FilaImportacionModel


class FilaImportacionSerializer(serializers.ModelSerializer):
    coincide_con_concepto = serializers.CharField(
        source="coincide_con.concepto", read_only=True, default=None, allow_null=True
    )

    class Meta:
        model = FilaImportacionModel
        fields = [
            "id",
            "numero",
            "fecha",
            "concepto",
            "importe",
            "accion",
            "coincide_con",
            "coincide_con_concepto",
            "movimiento",
        ]
        read_only_fields = fields
