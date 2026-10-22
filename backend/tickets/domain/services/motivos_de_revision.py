# tickets/domain/services/motivos_de_revision.py — por qué una persona tiene que mirar un ticket: lógica pura (módulos 74 y 88)
from datetime import date, timedelta
from decimal import Decimal

from tickets.domain.vo.datos_ticket import DatosTicket

TOLERANCIA_SUMA = Decimal("0.05")  # céntimos de redondeo entre la suma de las líneas y el total


def motivos_de_revision(datos: DatosTicket, *, hoy: date, umbral: float) -> list[str]:
    """Por qué una persona tiene que mirar el ticket antes de darlo por bueno. Vacío: el gasto se da por revisado."""
    motivos = []
    if datos.confianza < umbral:
        motivos.append(f"La IA no está segura ({datos.confianza:.2f}).")
    if datos.total is None:
        motivos.append("No se ha encontrado el total.")
    if datos.fecha is None:
        motivos.append("No se ha encontrado la fecha.")
    elif not hoy - timedelta(days=365) <= datos.fecha <= hoy:
        motivos.append("La fecha no es plausible.")
    if not datos.comercio:
        motivos.append("No se ha encontrado el comercio.")
    if datos.lineas and datos.total is not None:
        suma = sum(linea.importe for linea in datos.lineas)
        if abs(suma - datos.total) > TOLERANCIA_SUMA:
            motivos.append(f"Las líneas suman {suma:.2f} y el total es {datos.total}.")
    return motivos
