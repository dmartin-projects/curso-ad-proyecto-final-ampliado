# informes/infrastructure/api/v1/serializers/informe_serializer.py (módulos 78 y 88)
from rest_framework import serializers

from informes.infrastructure.database.models.informe_mensual_model import InformeMensual as InformeMensualModel


class InformeSerializer(serializers.ModelSerializer):
    mes = serializers.DateField(format="%Y-%m", read_only=True)
    automatico = serializers.SerializerMethodField()

    class Meta:
        model = InformeMensualModel
        fields = ["id", "mes", "tamano", "automatico", "creado", "actualizado"]
        read_only_fields = fields

    def get_automatico(self, informe) -> bool:
        return informe.generado_por_id is None
