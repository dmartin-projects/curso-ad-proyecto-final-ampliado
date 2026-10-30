# asistente/application/indexar_ayuda_use_case/indexar_ayuda_use_case.py — el índice, al día (módulo 100)
"""Incremental: cada trozo lleva la huella de su texto y el modelo con que se calculó su vector. Solo se vuelve a
embeber lo que ha cambiado (o lo que se calculó con otro modelo): cambiar una coma de la ayuda no recalcula cien trozos.

Y reconstruible: con `reconstruir`, se borra todo y se calcula de cero. El índice es una copia: la verdad son los .md.

Si los embeddings no están, se indexa igual, sin vectores (para buscar por texto); la próxima vez que estén, esos
trozos cuentan como "calculados con otro modelo" y se completan.

Ejercicio 2 del 102: con un `vigilante`, cada trozo nuevo o cambiado pasa por el clasificador de inyecciones antes de
entrar en el índice. La ayuda es nuestra y está en git, pero lo que entra en un índice de RAG lo lee el modelo como
contexto en cada búsqueda: un trozo envenenado (una contribución, un .md copiado de fuera) se queda fuera y se avisa."""

from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_input_dto import IndexarAyudaInputDTO
from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_output_dto import IndexarAyudaOutputDTO
from asistente.application.indexar_ayuda_use_case.i_indexar_ayuda_use_case import IIndexarAyudaUseCase
from asistente.application.ports.i_embeddings import IEmbeddings
from asistente.application.ports.i_fuente_de_ayuda import IFuenteDeAyuda
from asistente.application.seguridad.vigilante import Vigilante
from asistente.domain.exceptions.embeddings_no_disponibles_exception import EmbeddingsNoDisponiblesException
from asistente.domain.repositories.i_indice_de_ayuda import IIndiceDeAyuda
from asistente.domain.services.trocear import trocear
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo


class IndexarAyudaUseCase(IIndexarAyudaUseCase):
    def __init__(
        self,
        *,
        fuente: IFuenteDeAyuda,
        indice: IIndiceDeAyuda,
        embeddings: IEmbeddings | None,
        uow: IUnidadDeTrabajo,
        vigilante: Vigilante | None = None,
    ):
        self.fuente, self.indice, self.embeddings, self.uow = fuente, indice, embeddings, uow
        self.vigilante = vigilante

    def ejecutar(self, entrada: IndexarAyudaInputDTO) -> IndexarAyudaOutputDTO:
        trozos = [t for nombre, md in sorted(self.fuente.documentos().items()) for t in trocear(nombre, md)]
        if len({t.clave for t in trozos}) != len(trozos):
            raise ValueError("Dos secciones con el mismo título en un documento: la clave de un trozo es su sección.")
        with self.uow:
            if entrada.reconstruir:
                self.indice.borrar(list(self.indice.huellas()))
            guardadas = self.indice.huellas()
            modelo = self._modelo()
            cambiados = [t for t in trozos if guardadas.get(t.clave) != (t.huella, modelo)]
            rechazados = self._rechazados(cambiados)
            if rechazados:  # fuera del índice, como si no estuvieran en la ayuda (si ya estaban, se borran)
                trozos = [t for t in trozos if t.clave not in rechazados]
                cambiados = [t for t in cambiados if t.clave not in rechazados]
            vectores = None
            if cambiados and modelo:
                try:
                    vectores = self.embeddings.documentos([t.para_indexar for t in cambiados])
                except EmbeddingsNoDisponiblesException:
                    modelo = ""  # se guardan sin vector: la búsqueda por texto funciona igual
            self.indice.guardar(cambiados, vectores, modelo)
            sobran = sorted(set(guardadas) - {t.clave for t in trozos})
            self.indice.borrar(sobran)
        return IndexarAyudaOutputDTO(len(trozos), len(cambiados), len(sobran), modelo, tuple(sorted(rechazados)))

    def _rechazados(self, trozos) -> set[str]:
        if self.vigilante is None:
            return set()
        return {t.clave for t in trozos if self.vigilante.sospechoso(t.texto, f"ayuda:{t.clave}") is not None}

    def _modelo(self) -> str:
        if self.embeddings is None:
            return ""
        try:
            return self.embeddings.modelo
        except EmbeddingsNoDisponiblesException:
            return ""
