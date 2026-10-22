"""IAparcados en memoria (módulo 89). Como Kafka: lo aparcado NO se deshace con la transacción (por eso puede
aparcarse dos veces)."""

from estadisticas.application.ports.i_aparcados import IAparcados
from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO


class AparcadosFake(IAparcados):
    def __init__(self, *, caido: bool = False):
        self.caido = caido
        self.pendientes: list[tuple[MensajeInputDTO, Exception]] = []
        self.guardados: list[tuple[MensajeInputDTO, Exception]] = []

    def aparcar(self, mensaje: MensajeInputDTO, error: Exception) -> None:
        self.pendientes.append((mensaje, error))

    def confirmar(self) -> None:
        if self.caido:
            raise RuntimeError("No se pudieron guardar los mensajes aparcados")
        self.guardados += self.pendientes
        self.pendientes = []
