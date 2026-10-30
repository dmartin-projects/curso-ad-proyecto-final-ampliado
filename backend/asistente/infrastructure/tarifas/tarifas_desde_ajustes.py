# asistente/infrastructure/tarifas/tarifas_desde_ajustes.py — precios y cuotas, de los ajustes de Django (módulo 98)
from decimal import Decimal

from django.conf import settings

from asistente.application.ports.i_tarifas import ITarifas
from asistente.domain.vo.cuota import Cuota
from asistente.domain.vo.precio import Precio


class TarifasDesdeAjustes(ITarifas):
    def precio(self, modelo):
        p = settings.ASISTENTE_PRECIOS.get(modelo)
        return Precio(*(Decimal(x) for x in p)) if p else None

    def cuota(
        self, plan
    ):  # un plan sin cuota en los ajustes es un KeyError al arrancar la primera pregunta (y un test)
        c = settings.ASISTENTE_PLANES[str(plan)]
        return Cuota(tokens_dia_persona=int(c["tokens_dia_persona"]), coste_mes_hogar=Decimal(c["coste_mes_hogar"]))
