# asistente/domain/exceptions/asistente_no_disponible_exception.py (módulo 107)
from asistente.domain.vo.estado_del_asistente import APAGADO
from core.domain.exceptions.dominio_exception import DominioException

MENSAJES = {
    APAGADO: "El asistente está desactivado por mantenimiento. El resto de la app funciona con normalidad.",
}


class AsistenteNoDisponibleException(DominioException):
    """Un 503: no es culpa de quien pregunta, y vuelve. La app sin el asistente sigue entera (módulo 107)."""

    codigo = "asistente_no_disponible"
    status = 503
    mensaje = "El asistente no está disponible ahora mismo. Inténtalo en unos minutos."

    def __init__(self, motivo: str):
        super().__init__(MENSAJES.get(motivo, self.mensaje), motivo=motivo)
