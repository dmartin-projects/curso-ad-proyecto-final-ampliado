# tickets/infrastructure/ia/decimal_redondeado.py — un DecimalField que redondea lo que dice la IA (módulos 74 y 88)
from decimal import ROUND_HALF_UP, Decimal

from rest_framework import serializers


class DecimalRedondeado(serializers.DecimalField):
    """Redondea en vez de rechazar: un LLM devuelve 4.849999 donde el ticket dice 4,85.

    El parámetro `rounding` de DecimalField no basta: DRF comprueba los decimales ANTES de redondear.
    """

    def validate_precision(self, valor):
        return super().validate_precision(valor.quantize(Decimal(1).scaleb(-self.decimal_places), ROUND_HALF_UP))
