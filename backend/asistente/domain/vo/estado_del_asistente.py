# asistente/domain/vo/estado_del_asistente.py — si el asistente puede contestar ahora, y por qué no (módulo 107)
from dataclasses import dataclass

APAGADO = "apagado"  # lo ha apagado quien opera la app (ASISTENTE_ACTIVO): un incidente, un gasto que se dispara
SIN_MODELOS = "sin_modelos"  # todos los modelos de la cadena, con el circuito abierto: el proveedor no responde


@dataclass(frozen=True, slots=True)
class EstadoDelAsistente:
    activo: bool
    motivo: str = ""  # "" si está activo; APAGADO o SIN_MODELOS si no
