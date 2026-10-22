# importaciones/domain/services/resumen.py — lo que enseña la vista previa (módulos 75 y 88)
from importaciones.domain.bo.fila import Fila
from importaciones.domain.enums.accion import Accion


def resumen(filas: list[Fila]) -> dict:
    """Lo que enseña la vista previa. Los importes, como texto: van a un JSONField y al frontend sin perder céntimos."""
    duplicadas = sum(f.accion == Accion.DUPLICADA for f in filas)
    return {
        "desde": min(f.fecha for f in filas).isoformat(),
        "hasta": max(f.fecha for f in filas).isoformat(),
        "gastos": str(sum(f.importe for f in filas if f.importe < 0)),
        "ingresos": str(sum(f.importe for f in filas if f.importe > 0)),
        "duplicadas": duplicadas,
        "conciliar": sum(f.accion == Accion.CONCILIAR for f in filas),
        "a_importar": len(filas) - duplicadas,
    }
