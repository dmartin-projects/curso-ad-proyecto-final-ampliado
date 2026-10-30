"""Módulo 100: el buscador con fakes: híbrido, el fallback por texto, la reescritura y la reordenación."""

import json
import logging

from asistente.application.ayuda.buscador_de_ayuda import BuscadorDeAyuda
from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_input_dto import IndexarAyudaInputDTO
from asistente.application.indexar_ayuda_use_case.indexar_ayuda_use_case import IndexarAyudaUseCase
from asistente.application.tools.buscar_ayuda_tool import BuscarAyudaTool
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.infrastructure.ayuda.fuente_de_ayuda_en_disco import FuenteDeAyudaEnDisco
from asistente.tests.fakes.embeddings_fake import EmbeddingsFake
from asistente.tests.fakes.indice_de_ayuda_fake import IndiceDeAyudaFake
from asistente.tests.fakes.llm_fake import LLMFake
from asistente.tests.fakes.mundo import contexto
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake


def indice(embeddings=None) -> IndiceDeAyudaFake:
    i = IndiceDeAyudaFake()
    uso = IndexarAyudaUseCase(fuente=FuenteDeAyudaEnDisco(), indice=i, embeddings=embeddings, uow=UnidadDeTrabajoFake())
    uso.ejecutar(IndexarAyudaInputDTO())
    return i


def test_los_vectores_encuentran_lo_que_no_comparte_palabras():
    embeddings = EmbeddingsFake()
    b = BuscadorDeAyuda(indice=indice(embeddings), embeddings=embeddings, llm=None)
    r = b.buscar("quiero meter lo del banco")  # "banco" ≈ "extracto" para el fake
    assert r.modo == "híbrida" and "importar-extractos" in {p.fuente.split("#")[0] for p in r.pasajes}


def test_sin_embeddings_sigue_por_texto():
    b = BuscadorDeAyuda(indice=indice(EmbeddingsFake()), embeddings=EmbeddingsFake(caido=True), llm=None)
    r = b.buscar("passkey huella")
    assert r.modo == "texto" and r.pasajes[0].fuente == "seguridad-de-la-cuenta#Passkeys"


def test_la_reescritura_busca_con_las_palabras_de_la_ayuda():
    llm = LLMFake([LLMFake.responder("invitaciones enlace correo"), LLMFake.responder('{"relevantes": [1]}')])
    b = BuscadorDeAyuda(indice=indice(), embeddings=None, llm=llm)
    r = b.buscar("quiero que mi pareja vea las cuentas")
    assert r.consulta == "invitaciones enlace correo"
    assert "miembros-y-roles#Invitaciones" in [c.fuente for c in r.candidatos]  # con "pareja" sola, no salía
    assert r.pasajes == r.candidatos[:1] and len(r.llamadas) == 2  # el reordenador dijo [1]
    assert "pareja" in llm.peticiones[0].mensajes[0].texto and llm.peticiones[1].esquema.nombre == "pasajes_relevantes"


def test_la_reordenacion_manda_y_descarta_numeros_inventados():
    llm = LLMFake([LLMFake.responder("x"), LLMFake.responder('{"relevantes": [3, 99, 3, 1]}')])
    b = BuscadorDeAyuda(indice=indice(), embeddings=None, llm=llm, devolver=3)
    r = b.buscar("informe pdf mes")
    assert [p.clave for p in r.pasajes] == [r.candidatos[2].clave, r.candidatos[0].clave]


def test_si_ninguno_contesta_no_devuelve_nada():
    llm = LLMFake([LLMFake.responder("x"), LLMFake.responder('{"relevantes": []}')])
    assert BuscadorDeAyuda(indice=indice(), embeddings=None, llm=llm).buscar("informe pdf").pasajes == ()


def test_una_reordenacion_que_no_es_json_sigue_con_rrf_y_no_va_al_log(caplog):
    llm = LLMFake([LLMFake.responder("x"), LLMFake.responder("Los pasajes sobre la psiquiatra de Ana: 1 y 2")])
    with caplog.at_level(logging.WARNING):
        r = BuscadorDeAyuda(indice=indice(), embeddings=None, llm=llm).buscar("informe pdf mes")
    assert r.pasajes == r.candidatos[:3]
    assert "Reordenación no válida (45 caracteres)" in caplog.text and "psiquiatra" not in caplog.text


def test_sin_modelo_auxiliar_el_orden_de_rrf():
    llm = LLMFake([LLMNoDisponibleException("429"), LLMNoDisponibleException("429")])
    r = BuscadorDeAyuda(indice=indice(), embeddings=None, llm=llm).buscar("informe pdf mes")
    assert r.consulta == "" and r.pasajes == r.candidatos[:3] and r.llamadas == ()


def test_la_tool_cita_la_fuente_o_dice_que_no_hay_nada():
    llm = LLMFake([LLMFake.responder("ticket foto"), LLMFake.responder('{"relevantes": [1]}')])
    tool = BuscarAyudaTool(buscador=BuscadorDeAyuda(indice=indice(), embeddings=None, llm=llm))
    r = tool.ejecutar(contexto(), tool.validar(json.dumps({"pregunta": "¿cómo subo una foto del ticket?"})))
    assert r["pasajes"][0]["fuente"].startswith("tickets#") and "cita" in r["nota"]
    vacio = BuscarAyudaTool(buscador=BuscadorDeAyuda(indice=IndiceDeAyudaFake(), embeddings=None, llm=None))
    assert vacio.ejecutar(contexto(), vacio.validar('{"pregunta": "¿y esto?"}'))["pasajes"] == []
