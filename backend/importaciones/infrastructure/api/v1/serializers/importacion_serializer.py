# importaciones/infrastructure/api/v1/serializers/importacion_serializer.py (módulos 75 y 88)
from rest_framework import serializers

from importaciones.infrastructure.database.models.importacion_model import Importacion as ImportacionModel


class ImportacionSerializer(serializers.ModelSerializer):
    progreso = serializers.IntegerField(read_only=True)

    class Meta:
        model = ImportacionModel
        fields = [
            "id",
            "estado",
            "cuenta",
            "nombre_original",
            "formato",
            "total_filas",
            "procesadas",
            "progreso",
            "creados",
            "conciliados",
            "duplicados",
            "resumen",
            "avisos",
            "error",
            "creado",
            "terminado_en",
        ]
        read_only_fields = fields
