# importaciones/domain/enums/estado_importacion.py — el ciclo de vida de una importación (módulos 75 y 88)
#
# pendiente ─▶ analizando ─▶ vista_previa ─(confirmar)─▶ importando ─▶ completada ─(deshacer)─▶ deshecha
#                  └────────────────────────────────────────┴─▶ error ─(deshacer)─▶ deshecha
from enum import StrEnum


class EstadoImportacion(StrEnum):
    PENDIENTE = "pendiente"
    ANALIZANDO = "analizando"
    VISTA_PREVIA = "vista_previa"
    IMPORTANDO = "importando"
    COMPLETADA = "completada"
    ERROR = "error"
    DESHECHA = "deshecha"


E = EstadoImportacion
PUEDEN_FALLAR = (E.PENDIENTE, E.ANALIZANDO, E.IMPORTANDO)
