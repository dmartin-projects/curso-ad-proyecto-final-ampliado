# asistente/tests/fakes/mundo.py — un hogar, quien pregunta y el agente con fakes (módulos 94, 95 y 97)
from datetime import UTC, date, datetime

from asistente.application.agent.agente import Agente
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.agent.limites import Limites
from asistente.application.ayuda.buscador_de_ayuda import BuscadorDeAyuda
from asistente.application.chat.calculadora_de_graficos import CalculadoraDeGraficos
from asistente.application.tools.buscar_ayuda_tool import BuscarAyudaTool
from asistente.application.tools.buscar_movimientos_tool import BuscarMovimientosTool
from asistente.application.tools.comparar_con_ipc_tool import CompararConIpcTool
from asistente.application.tools.comparar_meses_tool import CompararMesesTool
from asistente.application.tools.detalle_ticket_tool import DetalleTicketTool
from asistente.application.tools.dias_festivos_tool import DiasFestivosTool
from asistente.application.tools.estado_presupuestos_tool import EstadoPresupuestosTool
from asistente.application.tools.exportar_tool import ExportarTool
from asistente.application.tools.gasto_por_categoria_tool import GastoPorCategoriaTool
from asistente.application.tools.grafico_tool import GraficoTool
from asistente.application.tools.listar_categorias_tool import ListarCategoriasTool
from asistente.application.tools.listar_cuentas_tool import ListarCuentasTool
from asistente.application.tools.listar_miembros_tool import ListarMiembrosTool
from asistente.application.tools.olvidar_tool import OlvidarTool
from asistente.application.tools.prevision_fin_de_mes_tool import PrevisionFinDeMesTool
from asistente.application.tools.proponer_movimiento_tool import ProponerMovimientoTool
from asistente.application.tools.recordar_tool import RecordarTool
from asistente.application.tools.resumen_mes_tool import ResumenMesTool
from asistente.application.tools.tendencia_tool import TendenciaTool
from asistente.application.tools.tipo_de_cambio_tool import TipoDeCambioTool
from asistente.application.tools.top_comercios_tool import TopComerciosTool
from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario
from asistente.domain.read_models.miembro_del_hogar import MiembroDelHogar
from asistente.tests.fakes.consultas_de_finanzas_fake import ConsultasDeFinanzasFake
from asistente.tests.fakes.exportador_de_movimientos_fake import ExportadorDeMovimientosFake
from asistente.tests.fakes.festivos_fake import FestivosFake
from asistente.tests.fakes.indice_de_ayuda_fake import IndiceDeAyudaFake
from asistente.tests.fakes.indice_de_precios_fake import IndiceDePreciosFake
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.membresias_fake import MembresiasFake
from asistente.tests.fakes.recuerdo_repositorio_fake import RecuerdoRepositorioFake
from asistente.tests.fakes.tickets_fake import TicketsFake
from asistente.tests.fakes.tipo_de_cambio_fake import TipoDeCambioFake
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


def membresias(hogar: HogarDelUsuario = CASA) -> MembresiasFake:
    fake = MembresiasFake({(ANA, hogar.id): hogar})
    fake.miembros_por_hogar[hogar.id] = (MiembroDelHogar("Ana", "admin"), MiembroDelHogar("Luis", "miembro"))
    return fake


def reloj(ahora: datetime | None = None) -> RelojFake:
    return RelojFake(HOY, ahora or datetime(2026, 10, 29, 10, 0, tzinfo=UTC))


def contexto(hogar: HogarDelUsuario = CASA, ahora: datetime | None = None) -> ContextoPregunta:
    return ContextoPregunta.abrir(usuario_id=ANA, hogar_id=hogar.id, membresias=membresias(hogar), reloj=reloj(ahora))


class Mundo:
    def __init__(self):
        self.finanzas = ConsultasDeFinanzasFake.de_casa(HOGAR)
        self.tickets = TicketsFake()
        self.divisas = TipoDeCambioFake()
        self.precios = IndiceDePreciosFake()
        self.festivos = FestivosFake()
        self.membresias = membresias()
        self.exportador = ExportadorDeMovimientosFake()
        self.cronometro = Cronometro()
        self.recuerdos = RecuerdoRepositorioFake()

    def tools(self):
        """Las dos del módulo 94."""
        return [ResumenMesTool(finanzas=self.finanzas), GastoPorCategoriaTool(finanzas=self.finanzas)]

    def catalogo(self, chat: bool = False):
        """Todas (módulos 95, 97 y 99), sobre los fakes: lo mismo que monta container.tools(chat) con los adapters."""
        f = self.finanzas
        consulta = [
            *self.tools(),
            CompararMesesTool(finanzas=f),
            BuscarMovimientosTool(finanzas=f),
            TendenciaTool(finanzas=f),
            TopComerciosTool(finanzas=f),
            EstadoPresupuestosTool(finanzas=f),
            PrevisionFinDeMesTool(finanzas=f),
            ListarCategoriasTool(finanzas=f),
            DetalleTicketTool(tickets=self.tickets),
            TipoDeCambioTool(divisas=self.divisas),
            CompararConIpcTool(finanzas=f, precios=self.precios),
            DiasFestivosTool(festivos=self.festivos),
            ListarCuentasTool(finanzas=f),
            ListarMiembrosTool(membresias=self.membresias),
        ]
        if not chat:
            return consulta
        return [
            *consulta,
            GraficoTool(calculadora=CalculadoraDeGraficos(consulta)),
            ExportarTool(finanzas=f, exportador=self.exportador),
            ProponerMovimientoTool(finanzas=f),
            RecordarTool(recuerdos=self.recuerdos, reloj=reloj()),  # módulo 99
            OlvidarTool(recuerdos=self.recuerdos, consultas=self.recuerdos),  # su ejercicio 1
            BuscarAyudaTool(buscador=BuscadorDeAyuda(indice=IndiceDeAyudaFake(), embeddings=None, llm=None)),  # 100
        ]

    def agente(self, guion: list, limites: Limites | None = None, tools=None) -> tuple[Agente, LLMFake]:
        llm = LLMFake(guion)
        agente = Agente(llm=llm, tools=tools or self.tools(), limites=limites, cronometro=self.cronometro)
        return agente, llm
