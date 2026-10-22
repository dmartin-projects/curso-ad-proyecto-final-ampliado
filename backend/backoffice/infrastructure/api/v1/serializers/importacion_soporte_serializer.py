# backoffice/infrastructure/api/v1/serializers/importacion_soporte_serializer.py (módulos 79 y 88)
from rest_framework import serializers

from importaciones.models import Importacion as ImportacionModel


class ImportacionSoporteSerializer(serializers.ModelSerializer):
    hogar_nombre = serializers.CharField(source="hogar.nombre", read_only=True)
    progreso = serializers.IntegerField(read_only=True)

    class Meta:
        model = ImportacionModel
        fields = [
            "id",
            "hogar",
            "hogar_nombre",
            "nombre_original",
            "estado",
            "progreso",
            "total_filas",
            "creados",
            "conciliados",
            "duplicados",
            "error",
            "creado",
        ]
        read_only_fields = fields
