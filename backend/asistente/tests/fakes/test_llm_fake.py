"""Módulo 93: el LLMFake cumple el port, sigue su guion y apunta lo que recibe."""

import pytest

from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.tests.fakes.llm_fake import GuionAgotadoError, LLMFake

PETICION = PeticionLLM(sistema="Responde breve.", mensajes=(Mensaje.usuario("¿Cuánto gastamos?"),))


def test_sigue_el_guion_en_orden_y_apunta_las_peticiones():
    llm = LLMFake([LLMFake.llamar("resumen_mes", mes="2026-09"), LLMFake.responder("812,40 €.")])

    primera, segunda = llm.generar(PETICION), llm.generar(PETICION)

    assert primera.motivo == MotivoFin.TOOLS
    assert (primera.llamadas[0].nombre, primera.llamadas[0].argumentos) == ("resumen_mes", '{"mes": "2026-09"}')
    assert (segunda.motivo, segunda.texto) == (MotivoFin.FIN, "812,40 €.")
    assert llm.peticiones == [PETICION, PETICION]


def test_un_paso_puede_ser_una_excepcion_o_una_funcion():
    llm = LLMFake([LLMNoDisponibleException("503"), lambda p: LLMFake.responder(p.mensajes[-1].texto.upper())])

    with pytest.raises(LLMNoDisponibleException):
        llm.generar(PETICION)
    assert llm.generar(PETICION).texto == "¿CUÁNTO GASTAMOS?"


def test_si_se_le_llama_de_mas_el_test_falla_con_un_mensaje_claro():
    llm = LLMFake([LLMFake.responder("hola")])
    llm.generar(PETICION)
    with pytest.raises(GuionAgotadoError, match="Llamada nº 2"):
        llm.generar(PETICION)


def test_argumentos_que_no_son_json_van_tal_cual():
    r = LLMFake.llamadas(("buscar", '{"texto": "Merca'), ("resumen_mes", {}))
    assert [ll.argumentos for ll in r.llamadas] == ['{"texto": "Merca', "{}"]
    assert [ll.id for ll in r.llamadas] == ["fake-0", "fake-1"]
