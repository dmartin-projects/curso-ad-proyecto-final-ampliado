# informes/infrastructure/api/v1/serializers/generar_informe_serializer.py (módulos 78 y 88)
from django.utils import timezone
from rest_framework import serializers

from core.domain.vo.mes import Mes
from core.infrastructure.api.serializers.regla import regla
from informes.domain.services.meses import comprobar_mes


class GenerarInformeSerializer(serializers.Serializer):
    mes = serializers.DateField(input_formats=["%Y-%m"], help_text="AAAA-MM")
    enviar = serializers.BooleanField(default=False, help_text="Enviarlo también por email a los miembros")

    def validate_mes(self, valor) -> Mes:
        return regla(comprobar_mes, Mes.de(valor), timezone.localdate())  # la regla es del dominio
