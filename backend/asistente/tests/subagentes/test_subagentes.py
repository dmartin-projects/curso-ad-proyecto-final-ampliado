"""Módulo 105: el orquestador y sus especialistas, con LLMFake: lo que ve cada uno, lo que vuelve y el análisis del
mes de punta a punta (sin Celery ni red)."""

import json

import pytest

from asistente.application.agent.agente import Agente
from asistente.application.analizar_mes_use_case.analizar_mes_use_case import AnalizarMesUseCase
from asistente.application.analizar_mes_use_case.dtos.analizar_mes_input_dto import AnalizarMesInputDTO
from asistente.application.pedir_analisis_use_case.dtos.pedir_analisis_input_dto import PedirAnalisisInputDTO
from asistente.application.pedir_analisis_use_case.pedir_analisis_use_case import PedirAnalisisUseCase
from asistente.application.ports.i_programador_de_analisis import IProgramadorDeAnalisis
from asistente.application.prompts.subagentes import ORQUESTADOR
from asistente.application.subagentes.especialistas import ESPECIALISTAS
from asistente.application.subagentes.instrucciones_de import instrucciones_de
from asistente.application.tools.subagente_tool import SubagenteTool
from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.exceptions.cuota_agotada_exception import CuotaAgotadaException
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.vo.consumo import Consumo
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.uso import Uso
from asistente.tests.fakes.avisos_de_progreso_fake import AvisosDeProgresoFake
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.consumo_repositorio_fake import ConsumoRepositorioFake
from asistente.tests.fakes.conversacion_command_repository_fake import ConversacionCommandRepositoryFake
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import ANA, HOGAR, SEPTIEMBRE, contexto, membresias, reloj
from asistente.tests.fakes.plan_del_hogar_repositorio_fake import PlanDelHogarRepositorioFake
from asistente.tests.fakes.tarifas_fake import TarifasFake
from core.domain.enums.rol import Rol
from core.domain.exceptions.validacion_exception import ValidacionException
from core.domain.vo.actor import Actor
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake

GASTOS = ESPECIALISTAS[0]
TAREA = "0b6f6a2e-6d2a-4c8e-9f5e-1a2b3c4d5e6f"


def montar(mundo, orquestador_guion, especialista_guion, observador=None):
    """El orquestador con el especialista en gastos, cada uno con su LLM falso."""
    especialista = LLMFake(especialista_guion)
    catalogo = {t.nombre: t for t in mundo.catalogo()}

    def crear(s):
        return Agente(
            llm=especialista,
            tools=[catalogo[n] for n in s.tools],
            observador=observador,
            sistema=instrucciones_de(s.instrucciones),
        )

    orquestador = LLMFake(orquestador_guion)
    agente = Agente(
        llm=orquestador,
        tools=[SubagenteTool(subagente=GASTOS, crear_agente=crear)],
        observador=observador,
        sistema=instrucciones_de(ORQUESTADOR),
    )
    return agente, orquestador, especialista


def test_el_especialista_solo_ve_su_encargo_su_papel_y_sus_tools(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    agente, orquestador, especialista = montar(
        mundo,
        [LLMFake.llamar("especialista_gastos", encargo="El gasto de septiembre de 2026"),
         LLMFake.responder("En septiembre, 776,59 €.")],
        [LLMFake.llamar("resumen_mes", mes="2026-09"), LLMFake.responder("Gastasteis 776,59 €.")],
    )  # fmt: skip

    r = agente.responder((Mensaje.usuario("Prepara el análisis de septiembre de 2026 (2026-09)."),), contexto())

    primera = especialista.peticiones[0]
    assert [m.texto for m in primera.mensajes] == ["El gasto de septiembre de 2026"]  # ni la pregunta ni el resto
    assert {t.nombre for t in primera.tools} == set(GASTOS.tools)
    assert "# Tu papel\nEres el especialista en el gasto" in primera.sistema
    assert "Hoy es jueves, 29 de octubre de 2026" in primera.sistema  # el contexto del hogar, el mismo
    assert {t.nombre for t in orquestador.peticiones[0].tools} == {"especialista_gastos"}  # sin tools de datos
    devuelto = json.loads(orquestador.peticiones[1].mensajes[-1].resultados[0].contenido)
    assert devuelto == {"especialista": "gastos", "informe": "Gastasteis 776,59 €.", "tools": ["resumen_mes"]}
    assert r.texto == "En septiembre, 776,59 €."


def test_un_especialista_que_no_termina_es_un_error_que_lee_el_orquestador(mundo):
    sin_terminar = [LLMFake.llamar("resumen_mes", mes=f"2026-0{i}") for i in range(1, 7)]
    agente, orquestador, _ = montar(
        mundo,
        [LLMFake.llamar("especialista_gastos", encargo="El gasto de septiembre"), LLMFake.responder("Sin datos.")],
        sin_terminar,
    )
    agente.responder((Mensaje.usuario("Analiza septiembre"),), contexto())
    error = orquestador.peticiones[1].mensajes[-1].resultados[0]
    assert error.es_error and "no ha terminado" in error.contenido


class Analisis:
    def __init__(self, mundo, orquestador_guion, especialista_guion):
        self.conversaciones, self.consumos = ConversacionCommandRepositoryFake(), ConsumoRepositorioFake()
        self.avisos = AvisosDeProgresoFake()
        self.caso = AnalizarMesUseCase(
            crear_orquestador=lambda obs: montar(mundo, orquestador_guion, especialista_guion, obs)[0],
            conversaciones=self.conversaciones,
            membresias=membresias(),
            avisos=self.avisos,
            consumos=self.consumos,
            tarifas=TarifasFake(),
            reloj=reloj(),
            uow=UnidadDeTrabajoFake(self.conversaciones),
        )

    def ejecutar(self):
        return self.caso.ejecutar(AnalizarMesInputDTO(ANA, HOGAR, "2026-09", TAREA))


def test_el_analisis_queda_como_conversacion_y_avisa_de_cada_paso(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    a = Analisis(
        mundo,
        [LLMFake.llamar("especialista_gastos", encargo="El gasto de septiembre"),
         LLMFake.responder("**Septiembre**: 776,59 €.")],
        [LLMFake.llamar("resumen_mes", mes="2026-09"), LLMFake.responder("776,59 €.")],
    )  # fmt: skip

    conversacion_id = a.ejecutar()

    assert a.avisos.pasos == ["Repartiendo el trabajo", "Analizando el gasto", "Listo: el gasto", "Análisis listo"]
    assert a.avisos.avisos[-1][3] == {"estado": "terminado", "paso": "Análisis listo", "conversacion": conversacion_id}
    conversacion = a.conversaciones.obtener(ANA, HOGAR, conversacion_id)
    assert conversacion.titulo == "Análisis de septiembre de 2026"
    assert conversacion.con_terceros  # un especialista es una tool de terceros: su informe puede citar lo que leyó
    pregunta, informe = a.conversaciones.visibles(conversacion_id)
    assert (pregunta.mensaje.rol, informe.texto) == (RolMensaje.USUARIO, "**Septiembre**: 776,59 €.")
    # Lo gastado: el orquestador (2 vueltas) y el especialista (2), en el canal del análisis
    (consumo,) = a.consumos.consumos
    assert (consumo.canal, consumo.uso) == (CanalDeConsumo.ANALISIS, Uso(400, 60))


def test_sin_modelo_el_aviso_es_un_fallo_y_no_queda_conversacion(mundo):
    a = Analisis(mundo, [LLMNoDisponibleException("429")], [])
    assert a.ejecutar() is None
    assert a.avisos.avisos[-1][3]["estado"] == "fallido"


class ProgramadorFake(IProgramadorDeAnalisis):
    def __init__(self):
        self.programados = []

    def programar(self, usuario_id, hogar_id, mes, tarea):
        self.programados.append((usuario_id, hogar_id, mes, tarea))


def pedir(mes=None, tarea=TAREA, planes=None):
    programador = ProgramadorFake()
    caso = PedirAnalisisUseCase(
        membresias=membresias(),
        programador=programador,
        planes=planes or PlanDelHogarRepositorioFake(),
        tarifas=TarifasFake(),
        consumos=ConsumoRepositorioFake(),
        reloj=reloj(),
    )
    return caso.ejecutar(PedirAnalisisInputDTO(HOGAR, Actor(ANA, Rol.LECTOR), tarea, mes)), programador


def test_pedir_el_analisis_lo_programa_con_su_tarea():
    mes, programador = pedir()
    assert (mes, programador.programados) == ("2026-10", [(ANA, HOGAR, "2026-10", TAREA)])


@pytest.mark.parametrize(("mes", "tarea"), [("2026-11", TAREA), ("octubre", TAREA), (None, "no-es-un-uuid")])
def test_un_mes_futuro_o_mal_escrito_o_una_tarea_que_no_es_un_uuid(mes, tarea):
    with pytest.raises(ValidacionException):
        pedir(mes, tarea)


def test_sin_cuota_no_se_programa(monkeypatch):
    consumos = ConsumoRepositorioFake()
    consumos.anotar([Consumo(ANA, HOGAR, CanalDeConsumo.CHAT, "fake", Uso(10_000_000, 0), None, reloj().ahora())])
    caso = PedirAnalisisUseCase(
        membresias=membresias(), programador=ProgramadorFake(), planes=PlanDelHogarRepositorioFake(),
        tarifas=TarifasFake(), consumos=consumos, reloj=reloj(),
    )  # fmt: skip
    with pytest.raises(CuotaAgotadaException):
        caso.ejecutar(PedirAnalisisInputDTO(HOGAR, Actor(ANA, Rol.LECTOR), TAREA))
