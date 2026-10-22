# finanzas/infrastructure/api/v1/serializers/movimiento_serializer.py (módulos 33, 87 y 88)
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from core.domain.vo.dinero import Dinero
from core.infrastructure.api.serializers.a_dominio_mixin import ADominioMixin
from core.infrastructure.api.serializers.regla import regla
from finanzas.domain.bo.movimiento import comprobar_fecha, comprobar_importe
from finanzas.infrastructure.api.v1.serializers.comercio_serializer import ComercioSerializer
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel
from finanzas.infrastructure.database.models.cuenta_model import Cuenta as CuentaModel
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel
from hogares.infrastructure.api.base.del_hogar_mixin import DelHogarMixin


class MovimientoSerializer(DelHogarMixin, ADominioMixin, serializers.ModelSerializer):
    campos_del_hogar = {"cuenta": CuentaModel, "categoria": CategoriaModel}
    relaciones = {"cuenta": "cuenta_id", "categoria": "categoria_id"}
    cuenta_nombre = serializers.CharField(source="cuenta.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True, default=None, allow_null=True)
    categoria_color = serializers.CharField(source="categoria.color", read_only=True, default=None, allow_null=True)
    comercio = ComercioSerializer(read_only=True)
    num_adjuntos = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = MovimientoModel
        fields = [
            "id",
            "fecha",
            "importe",
            "concepto",
            "cuenta",
            "cuenta_nombre",
            "categoria",
            "categoria_nombre",
            "categoria_color",
            "comercio",
            "etiquetas",
            "notas",
            "origen",
            "revisado",
            "num_adjuntos",
            "creado",
        ]
        read_only_fields = ["origen", "creado"]

    # Las reglas son del dominio; aquí solo se llaman, para que la API dé TODOS los errores a la vez. Las etiquetas
    # las normaliza el BO (Movimiento.__post_init__)
    def validate_importe(self, valor: Decimal) -> Decimal:
        regla(comprobar_importe, Dinero(valor))
        return valor

    def validate_fecha(self, valor):
        return regla(comprobar_fecha, valor, timezone.localdate())
