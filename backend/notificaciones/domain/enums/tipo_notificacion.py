# notificaciones/domain/enums/tipo_notificacion.py (módulos 76 y 88)
from enum import StrEnum


class TipoNotificacion(StrEnum):
    TICKET_PROCESADO = "ticket_procesado"
    TICKET_REVISAR = "ticket_revisar"
    TICKET_ERROR = "ticket_error"
    IMPORTACION_LISTA = "importacion_lista"
    IMPORTACION_COMPLETADA = "importacion_completada"
    IMPORTACION_ERROR = "importacion_error"
    PRESUPUESTO_SUPERADO = "presupuesto_superado"
    INFORME_LISTO = "informe_listo"
