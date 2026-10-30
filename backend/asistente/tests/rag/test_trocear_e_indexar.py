"""Módulo 100: la ayuda en trozos, el índice incremental y reconstruible, y la fusión de búsquedas."""

import pytest

from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_input_dto import IndexarAyudaInputDTO
from asistente.application.indexar_ayuda_use_case.indexar_ayuda_use_case import IndexarAyudaUseCase
from asistente.application.ports.i_fuente_de_ayuda import IFuenteDeAyuda
from asistente.domain.services.fusion_rrf import fusionar
from asistente.domain.services.normalizar import sin_tildes
from asistente.domain.services.trocear import MAX_CARACTERES, trocear
from asistente.infrastructure.ayuda.fuente_de_ayuda_en_disco import FuenteDeAyudaEnDisco
from asistente.tests.fakes.embeddings_fake import EmbeddingsFake
from asistente.tests.fakes.indice_de_ayuda_fake import IndiceDeAyudaFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake

MD = """---
titulo: Tickets
actualizado: 2026-10-30
---

## Subir un ticket

Sube la foto.

## Cuándo hay que revisarlo

Si la IA no está segura, queda Por revisar.
"""


class Fuente(IFuenteDeAyuda):
    def __init__(self, documentos):
        self.docs = documentos

    def documentos(self):
        return dict(self.docs)


def test_un_trozo_por_seccion_con_el_titulo_delante():
    trozos = trocear("tickets", MD)
    assert [t.clave for t in trozos] == ["tickets#Subir un ticket#1", "tickets#Cuándo hay que revisarlo#1"]
    assert trozos[0].para_indexar == "Tickets. Subir un ticket. Sube la foto."
    assert trozos[1].fuente == "tickets#Cuándo hay que revisarlo"


def test_una_seccion_larga_se_parte_por_parrafos():
    parrafos = "\n\n".join(f"Párrafo {n}. " + "x" * 500 for n in range(4))
    trozos = trocear("largo", f"## Sección\n\n{parrafos}\n")
    assert [t.parte for t in trozos] == [1, 2]
    assert all(len(t.texto) <= MAX_CARACTERES for t in trozos) and trozos[1].texto.startswith("Párrafo 2.")


def test_la_ayuda_de_verdad_se_trocea_sin_claves_repetidas():
    trozos = [t for nombre, md in FuenteDeAyudaEnDisco().documentos().items() for t in trocear(nombre, md)]
    assert len(trozos) >= 30 and len({t.clave for t in trozos}) == len(trozos)
    assert all(t.titulo != t.documento for t in trozos), "un .md sin cabecera"


def caso(docs, embeddings=None):
    indice = IndiceDeAyudaFake()
    uso = IndexarAyudaUseCase(fuente=Fuente(docs), indice=indice, embeddings=embeddings, uow=UnidadDeTrabajoFake())
    return uso, indice


def test_indexar_es_incremental():
    embeddings = EmbeddingsFake()
    docs = {"tickets": MD}
    uso, indice = caso(docs, embeddings)
    assert uso.ejecutar(IndexarAyudaInputDTO()).nuevos_o_cambiados == 2
    antes = embeddings.llamadas
    docs["tickets"] = MD.replace("Sube la foto.", "Sube la foto o el PDF.")
    r = uso.ejecutar(IndexarAyudaInputDTO())
    assert (r.nuevos_o_cambiados, r.borrados, embeddings.llamadas - antes) == (1, 0, 1)  # solo el que cambió
    docs["tickets"] = MD.split("## Cuándo")[0]
    assert uso.ejecutar(IndexarAyudaInputDTO()).borrados == 1


def test_otro_modelo_lo_recalcula_todo_y_sin_modelo_se_indexa_igual():
    docs = {"tickets": MD}
    sin, indice = caso(docs, EmbeddingsFake(caido=True))
    r = sin.ejecutar(IndexarAyudaInputDTO())
    assert (r.trozos, r.modelo) == (2, "") and all(m == "" for _, m in indice.huellas().values())
    con = IndexarAyudaUseCase(
        fuente=Fuente(docs), indice=indice, embeddings=EmbeddingsFake("otro"), uow=UnidadDeTrabajoFake()
    )
    assert con.ejecutar(IndexarAyudaInputDTO()).nuevos_o_cambiados == 2  # ahora sí tienen vector
    assert con.ejecutar(IndexarAyudaInputDTO(reconstruir=True)).nuevos_o_cambiados == 2


def test_dos_secciones_iguales_en_un_documento_no():
    with pytest.raises(ValueError, match="mismo título"):
        caso({"x": "## A\n\nuno\n\n## A\n\ndos\n"})[0].ejecutar(IndexarAyudaInputDTO())


def test_rrf_premia_lo_que_sale_arriba_en_las_dos():
    # c (3º y 1º: 1/63 + 1/61) gana por poco a b (2º en las dos: 2/62); a y d, en una sola
    assert fusionar([["a", "b", "c"], ["c", "b", "d"]]) == ["c", "b", "a", "d"]
    assert fusionar([["a", "b"], ["b", "a"], ["b"]]) == ["b", "a"]


def test_sin_tildes_pero_con_enie():
    assert sin_tildes("Común, AÑO y pingüino") == "comun, año y pinguino"
