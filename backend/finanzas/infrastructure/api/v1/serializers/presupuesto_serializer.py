# finanzas/infrastructure/api/v1/serializers/presupuesto_serializer.py (módulos 76 y 87)
#
# Sin validate_mes, validate_importe ni el duplicado: un Presupuesto del dominio es de un Mes, su importe lo comprueba
# el BO y el duplicado lo traduce el command repository desde la constraint.
from rest_framework import serializers

from core.infrastructure.api.serializers.a_dominio_mixin import ADominioMixin
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel
from finanzas.infrastructure.database.models.presupuesto_model import Presupuesto as PresupuestoModel
from hogares.api.base import DelHogarMixin


class PresupuestoSerializer(DelHogarMixin, ADominioMixin, serializers.ModelSerializer):
    campos_del_hogar = {"categoria": CategoriaModel}
    relaciones = {"categoria": "categoria_id"}
    gastado = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    porcentaje = serializers.SerializerMethodField()

    class Meta:
        model = PresupuestoModel
        fields = ["id", "categoria", "mes", "importe", "gastado", "porcentaje"]

    def get_porcentaje(self, p) -> int | None:
        gastado = getattr(p, "gastado", None)
        return None if gastado is None else int(abs(gastado) / p.importe * 100)
