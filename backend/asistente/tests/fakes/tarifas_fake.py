# asistente/tests/fakes/tarifas_fake.py (módulo 98)
from decimal import Decimal

from asistente.application.ports.i_tarifas import ITarifas
from asistente.domain.enums.plan import Plan
from asistente.domain.vo.cuota import Cuota
from asistente.domain.vo.precio import Precio

# Los de Groq para gpt-oss-120b (USD por millón): las cuentas de los tests salen como en producción
PRECIOS = {"openai/gpt-oss-120b": Precio(Decimal("0.15"), Decimal("0.60"), Decimal("0.075"))}
CUOTAS = {
    Plan.BASICO: Cuota(tokens_dia_persona=5000, coste_mes_hogar=Decimal("0.01")),
    Plan.PLUS: Cuota(tokens_dia_persona=100_000, coste_mes_hogar=Decimal("5")),
}


class TarifasFake(ITarifas):
    def precio(self, modelo):
        return PRECIOS.get(modelo)

    def cuota(self, plan):
        return CUOTAS[plan]
