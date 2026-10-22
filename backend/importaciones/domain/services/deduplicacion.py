# importaciones/domain/services/deduplicacion.py — qué se hace con cada fila del extracto (módulos 75 y 88)
#
# Lógica pura: el use case pide los datos a finanzas (las huellas que ya existen, los gastos sin conciliar) y la
# decisión (duplicada, conciliar, crear) se toma aquí, con datos en memoria: se prueba sin base de datos.
import hashlib
from collections import Counter
from collections.abc import Iterable
from datetime import date, timedelta
from decimal import Decimal

from core.domain.services.normalizacion import normalizar
from importaciones.domain.bo.fila import Fila
from importaciones.domain.enums.accion import Accion
from importaciones.domain.vo.candidato import Candidato
from importaciones.domain.vo.fila_leida import FilaLeida


def huellas(cuenta_id: int, filas: list[FilaLeida]) -> list[str]:
    """sha256(cuenta | fecha | importe | concepto normalizado | nº de ocurrencia).

    El nº de ocurrencia distingue dos movimientos idénticos legítimos (dos cafés de 1,50 € el mismo día
    en el mismo bar): el primero es #1 y el segundo #2, en este extracto y en cualquier otro que los incluya.
    """
    vistas: Counter = Counter()
    resultado = []
    for fila in filas:
        base = (cuenta_id, fila.fecha.isoformat(), f"{fila.importe:.2f}", normalizar(fila.concepto))
        vistas[base] += 1
        texto = "|".join(map(str, (*base, vistas[base])))
        resultado.append(hashlib.sha256(texto.encode()).hexdigest())
    return resultado


def _emparejar(candidatos: list[Candidato], fecha: date, margen: timedelta) -> Candidato | None:
    """El de fecha más cercana dentro del margen; se retira para no emparejarlo con dos filas."""
    cercanos = [c for c in candidatos if abs(c.fecha - fecha) <= margen]
    if not cercanos:
        return None
    mejor = min(cercanos, key=lambda c: abs(c.fecha - fecha))
    candidatos.remove(mejor)
    return mejor


def clasificar(
    leidas: list[FilaLeida],
    huellas_de_las_filas: list[str],
    existentes: set[str],
    candidatos: Iterable[Candidato],
    margen: timedelta,
) -> list[Fila]:
    """Cada fila: DUPLICADA (ya importada), CONCILIAR (coincide con un gasto que ya estaba) o CREAR."""
    por_importe: dict[Decimal, list[Candidato]] = {}
    for c in candidatos:
        por_importe.setdefault(c.importe, []).append(c)
    filas = []
    for leida, huella in zip(leidas, huellas_de_las_filas, strict=True):
        fila = Fila(leida.numero, leida.fecha, leida.concepto, leida.importe, huella, Accion.CREAR)
        if huella in existentes:
            fila.accion = Accion.DUPLICADA
        elif c := _emparejar(por_importe.get(leida.importe, []), leida.fecha, margen):
            fila.accion, fila.coincide_con_id = Accion.CONCILIAR, c.movimiento_id
        filas.append(fila)
    return filas


def repartir(filas: list[Fila], ya_importadas: set[str]) -> tuple[list[Fila], list[Fila], list[Fila]]:
    """Al importar un lote: (duplicadas, a conciliar, a crear). Entre el análisis y la importación, otro extracto
    solapado puede haber creado alguna fila: esas son duplicadas. Una fila a conciliar cuyo gasto ya no existe, se crea.
    """
    duplicadas, conciliar, crear = [], [], []
    for fila in filas:
        if fila.huella in ya_importadas:
            fila.accion = Accion.DUPLICADA
            duplicadas.append(fila)
        elif fila.accion == Accion.CONCILIAR and fila.coincide_con_id is not None:
            conciliar.append(fila)
        else:
            fila.accion = Accion.CREAR
            crear.append(fila)
    return duplicadas, conciliar, crear
