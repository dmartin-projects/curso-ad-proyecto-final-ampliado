# asistente/application/chat/observador_del_chat.py — cada paso del agente, convertido en eventos del chat (módulos 97 y 99)
from collections.abc import Callable
from typing import Any

from asistente.application.chat.artefactos import archivo_a_datos, grafico_a_datos
from asistente.application.chat.etiquetas import ETIQUETAS
from asistente.application.ports.i_almacen_de_archivos import IAlmacenDeArchivos
from asistente.application.ports.i_emisor_de_eventos import IEmisorDeEventos
from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.domain.exceptions.pregunta_cancelada_exception import PreguntaCanceladaException
from asistente.domain.vo.archivo_exportado import ArchivoExportado
from asistente.domain.vo.grafico import Grafico
from asistente.domain.vo.propuesta_preparada import PropuestaPreparada
from asistente.domain.vo.recuerdo_guardado import RecuerdoGuardado


class ObservadorDelChat(IObservadorAgente):
    """Escucha al agente y habla con la interfaz (por el emisor): qué tool está mirando, cada trozo de texto, los
    gráficos, archivos y propuestas. Y es el que corta: en cada paso mira si la persona sigue ahí; si no, lanza
    PreguntaCanceladaException, que sale del bucle y de la llamada en streaming (no se pagan más vueltas)."""

    def __init__(
        self,
        emisor: IEmisorDeEventos,
        almacen: IAlmacenDeArchivos,
        guardar_propuesta: Callable[[PropuestaPreparada], dict[str, Any]],
        ligar_archivo: Callable[[str], None] = lambda ruta: None,
    ):
        """`ligar_archivo(ruta)`: un archivo recién guardado, a la conversación ya (si no, una pregunta que se cancela
        después de exportar dejaría un CSV con movimientos del hogar que nada borra)."""
        self.emisor, self.almacen, self.guardar_propuesta = emisor, almacen, guardar_propuesta
        self.ligar_archivo = ligar_archivo
        self.graficos: list[dict] = []
        self.archivos: list[dict] = []
        self.propuestas: list[dict] = []
        self.recuerdos: list[dict] = []  # módulo 99

    def comprobar(self) -> None:
        if self.emisor.cancelado():
            raise PreguntaCanceladaException()

    def texto(self, trozo: str) -> None:
        """El `al_texto` del agente: cada trozo de la respuesta, según lo escribe el modelo."""
        self.comprobar()
        self.emisor.emitir("texto", {"delta": trozo})

    def respuesta(self, respuesta):
        self.comprobar()

    def llamada(self, llamada):
        self.comprobar()
        self.emisor.emitir("tool", {"nombre": llamada.nombre, "texto": ETIQUETAS.get(llamada.nombre, "Consultando")})

    def resultado(self, resultado, duracion_ms):
        self.comprobar()  # antes de la siguiente vuelta: si se ha ido, esa llamada al modelo ya no se hace

    def artefacto(self, artefacto):
        if isinstance(artefacto, Grafico):
            datos = grafico_a_datos(artefacto)
            self.graficos.append(datos)
            self.emisor.emitir("grafico", datos)
        elif isinstance(artefacto, ArchivoExportado):
            self.ligar_archivo(artefacto.ruta)
            datos = archivo_a_datos(artefacto)
            self.archivos.append(datos)
            self.emisor.emitir("archivo", {**datos, "url": self.almacen.url(artefacto.ruta)})
        elif isinstance(artefacto, RecuerdoGuardado):  # módulo 99: "lo recordaré", con su botón de olvidar
            datos = {"id": artefacto.id, "texto": artefacto.texto}
            self.recuerdos.append(datos)
            self.emisor.emitir("recuerdo", datos)
        elif isinstance(artefacto, PropuestaPreparada):
            datos = self.guardar_propuesta(artefacto)  # con su id: la interfaz la confirma por él
            self.propuestas.append(datos)
            self.emisor.emitir("propuesta", {**datos, "estado": "pendiente"})
