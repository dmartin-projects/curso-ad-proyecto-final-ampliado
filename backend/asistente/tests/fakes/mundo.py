# asistente/tests/fakes/mundo.py — un hogar, quien pregunta y el agente con fakes (módulo 94)
from datetime import UTC, date, datetime

from asistente.application.agent.agente import Agente
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.agent.limites import Limites
from asistente.application.tools.gasto_por_categoria_tool import GastoPorCategoriaTool
from asistente.application.tools.resumen_mes_tool import ResumenMesTool
from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario
from asistente.tests.fakes.consultas_de_finanzas_fake import ConsultasDeFinanzasFake
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.membresias_fake import MembresiasFake
from core.domain.vo.mes import Mes
from core.tests.fakes.reloj_fake import RelojFake

HOY = date(2026, 10, 29)
ANA, HOGAR = 7, 3
CASA = HogarDelUsuario(id=HOGAR, nombre="Casa de Ana y Luis", moneda="EUR", zona_horaria="Europe/Madrid", rol="admin")
SEPTIEMBRE, OCTUBRE = Mes(2026, 9), Mes(2026, 10)


class Cronometro:
    """Un reloj de segundos que avanza solo cuando el test lo dice (o un tanto por cada lectura)."""

    def __init__(self, paso: float = 0.0):
        self.segundos, self.paso = 0.0, paso

    def __call__(self) -> float:
        self.segundos += self.paso
        return self.segundos


def contexto(hogar: HogarDelUsuario = CASA, ahora: datetime | None = None) -> ContextoPregunta:
    reloj = RelojFake(HOY, ahora or datetime(2026, 10, 29, 10, 0, tzinfo=UTC))
    return ContextoPregunta.abrir(
        usuario_id=ANA, hogar_id=hogar.id, membresias=MembresiasFake({(ANA, hogar.id): hogar}), reloj=reloj
    )


class Mundo:
    def __init__(self):
        self.finanzas = ConsultasDeFinanzasFake()
        self.cronometro = Cronometro()

    def tools(self):
        return [ResumenMesTool(finanzas=self.finanzas), GastoPorCategoriaTool(finanzas=self.finanzas)]

    def agente(self, guion: list, limites: Limites | None = None, tools=None) -> tuple[Agente, LLMFake]:
        llm = LLMFake(guion)
        agente = Agente(llm=llm, tools=tools or self.tools(), limites=limites, cronometro=self.cronometro)
        return agente, llm
