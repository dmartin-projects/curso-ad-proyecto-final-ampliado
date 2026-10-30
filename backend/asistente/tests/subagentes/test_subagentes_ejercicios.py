"""Los ejercicios del 105: cancelar entre especialista y especialista, el tope de tokens de todo el análisis y uno a la
vez por persona y hogar."""

import uuid

import pytest
from django.core.cache import cache

from asistente.application.analizar_mes_use_case.analizar_mes_use_case import AnalizarMesUseCase
from asistente.application.analizar_mes_use_case.dtos.analizar_mes_input_dto import AnalizarMesInputDTO
from asistente.application.ports.i_control_de_analisis import IControlDeAnalisis
from asistente.domain.exceptions.analisis_en_curso_exception import AnalisisEnCursoException
from asistente.infrastructure.cache.control_de_analisis_en_cache import ControlDeAnalisisEnCache
from asistente.tests.fakes.avisos_de_progreso_fake import AvisosDeProgresoFake
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.consumo_repositorio_fake import ConsumoRepositorioFake
from asistente.tests.fakes.conversacion_command_repository_fake import ConversacionCommandRepositoryFake
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import ANA, HOGAR, SEPTIEMBRE, membresias, reloj
from asistente.tests.fakes.tarifas_fake import TarifasFake
from asistente.tests.subagentes.test_subagentes import TAREA, montar, pedir
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake


class ControlFake(IControlDeAnalisis):
    def __init__(self, cancelar_tras: int | None = None):
        self.en_curso: set = set()
        self.consultas, self.cancelar_tras = 0, cancelar_tras

    def empezar(self, usuario_id, hogar_id, tarea):
        if (usuario_id, hogar_id) in self.en_curso:
            return False
        self.en_curso.add((usuario_id, hogar_id))
        return True

    def terminar(self, usuario_id, hogar_id):
        self.en_curso.discard((usuario_id, hogar_id))

    def cancelar(self, usuario_id, tarea):
        self.cancelar_tras = 0

    def cancelado(self, usuario_id, tarea):
        self.consultas += 1
        return self.cancelar_tras is not None and self.consultas > self.cancelar_tras


def analisis(mundo, control, max_tokens=None, especialistas=2):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, gastos="776.59")
    encargos = [LLMFake.llamar("especialista_gastos", encargo=f"Encargo número {i}") for i in range(especialistas)]
    trabajo = [LLMFake.llamar("resumen_mes", mes="2026-09"), LLMFake.responder("776,59 €.")] * especialistas
    avisos, consumos = AvisosDeProgresoFake(), ConsumoRepositorioFake()
    caso = AnalizarMesUseCase(
        crear_orquestador=lambda obs: montar(mundo, [*encargos, LLMFake.responder("Informe.")], trabajo, obs)[0],
        conversaciones=ConversacionCommandRepositoryFake(),
        membresias=membresias(),
        avisos=avisos,
        consumos=consumos,
        tarifas=TarifasFake(),
        reloj=reloj(),
        uow=UnidadDeTrabajoFake(),
        control=control,
        max_tokens=max_tokens,
    )
    return caso.ejecutar(AnalizarMesInputDTO(ANA, HOGAR, "2026-09", TAREA)), avisos, consumos


def test_cancelado_para_antes_del_siguiente_especialista_y_lo_gastado_se_anota(mundo):
    control = ControlFake(cancelar_tras=1)  # la persona cancela mientras trabaja el primero
    conversacion, avisos, consumos = analisis(mundo, control)
    assert conversacion is None
    assert avisos.pasos == ["Repartiendo el trabajo", "Analizando el gasto", "Listo: el gasto", "Análisis cancelado."]
    assert avisos.avisos[-1][3]["estado"] == "cancelado"
    assert consumos.consumos  # el orquestador y el primer especialista ya se habían pagado
    assert control.en_curso == set()  # y se puede pedir otro


def test_el_tope_de_tokens_cuenta_al_orquestador_y_a_los_especialistas(mundo):
    # Con LLMFake, una tool call son 110 tokens y una respuesta 120: tras el primer especialista, 110 + 110 + 120 = 340
    conversacion, avisos, _ = analisis(mundo, ControlFake(), max_tokens=300)
    assert conversacion is None
    assert avisos.avisos[-1][3] == {
        "estado": "fallido",
        "paso": "El análisis ha llegado a su tope de tokens sin terminar.",
    }


def test_sin_tope_ni_cancelacion_termina(mundo):
    conversacion, avisos, _ = analisis(mundo, ControlFake(), max_tokens=10_000)
    assert conversacion is not None and avisos.avisos[-1][3]["estado"] == "terminado"


def test_dos_a_la_vez_no_y_al_terminar_si():
    control = ControlFake()
    mes, _ = pedir(control=control)
    with pytest.raises(AnalisisEnCursoException):
        pedir(control=control, tarea=str(uuid.uuid4()))
    control.terminar(ANA, HOGAR)
    pedir(control=control, tarea=str(uuid.uuid4()))


def test_el_control_en_la_cache_de_cada_persona():
    cache.clear()
    control = ControlDeAnalisisEnCache()
    assert control.empezar(7, 3, "a") is True
    assert control.empezar(7, 3, "b") is False  # la misma persona, el mismo hogar
    assert control.empezar(8, 3, "c") is True  # otra persona
    control.terminar(7, 3)
    assert control.empezar(7, 3, "d") is True
    control.cancelar(8, "a")  # alguien que sabe el id de la tarea de otro: no le afecta
    assert (control.cancelado(7, "a"), control.cancelado(8, "a")) == (False, True)
