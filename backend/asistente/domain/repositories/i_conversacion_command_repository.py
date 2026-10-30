# asistente/domain/repositories/i_conversacion_command_repository.py — escribir conversaciones (módulo 97)
from abc import ABC, abstractmethod

from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion


class IConversacionCommandRepository(ABC):
    """La conversación y su historial. El historial solo crece: se añaden mensajes y, como mucho, se marca una
    pregunta como incompleta (cancelada o fallida); nunca se reescribe."""

    @abstractmethod
    def obtener(self, usuario_id: int, hogar_id: int, conversacion_id: int) -> Conversacion:
        """La de esa persona en ese hogar, o ConversacionNoEncontradaException."""

    @abstractmethod
    def guardar(self, conversacion: Conversacion) -> None:
        """Crea o actualiza (pone el id) y la marca como actualizada ahora: sube al principio de la lista."""

    @abstractmethod
    def eliminar(self, conversacion: Conversacion) -> None: ...

    @abstractmethod
    def archivos(self, conversacion_id: int) -> tuple[str, ...]:
        """Las rutas en el almacenamiento de lo que la conversación ha guardado: los adjuntos y los CSV exportados."""

    @abstractmethod
    def ligar_archivo(self, mensaje_id: int, ruta: str) -> None:
        """Un archivo que una pregunta acaba de guardar (un CSV exportado), ligado a ella EN CUANTO existe: si la
        pregunta se cancela o falla después, `archivos` lo sigue encontrando (para borrarlo con la conversación)."""

    @abstractmethod
    def historial(self, conversacion_id: int) -> tuple[Mensaje, ...]:
        """Lo que se reenvía al modelo: todos los mensajes, en orden, menos las preguntas incompletas."""

    @abstractmethod
    def anadir(self, conversacion_id: int, mensajes: list[MensajeDeConversacion]) -> list[int]:
        """Al final del historial; devuelve sus ids."""

    @abstractmethod
    def marcar_incompleto(self, mensaje_id: int, motivo: str) -> None:
        """La pregunta se cancela o falla: se sigue viendo, pero ya no viaja al modelo (dejaría dos preguntas
        seguidas sin respuesta en el historial)."""
