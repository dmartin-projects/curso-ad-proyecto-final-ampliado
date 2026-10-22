# tickets/infrastructure/api/v1/serializers/confirmar_ticket_serializer.py (módulos 74 y 88)
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from core.infrastructure.api.serializers.a_dominio_mixin import ADominioMixin
from finanzas.models import Categoria
from hogares.infrastructure.api.base.del_hogar_mixin import DelHogarMixin


class ConfirmarTicketSerializer(DelHogarMixin, ADominioMixin, serializers.Serializer):
    campos_del_hogar = {"categoria": Categoria}
    relaciones = {"categoria": "categoria_id"}
    fecha = serializers.DateField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    concepto = serializers.CharField(max_length=255)
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.none(), allow_null=True, required=False)

    def validate_fecha(self, valor):
        if valor > timezone.localdate():
            raise serializers.ValidationError("La fecha no puede ser futura.")
        return valor
