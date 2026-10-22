# importaciones/domain/services/saldos.py — los saldos de un extracto deben cuadrar (módulos 75 y 88)
from importaciones.domain.vo.lectura import Lectura


def comprobar_saldos(lectura: Lectura) -> None:
    """Si hay saldo, cada fila debe cuadrar con la anterior: detecta filas mal leídas o que faltan.

    Una regla del extracto, no del formato: vale igual para un CSV que para un PDF.
    """
    anterior = None
    for fila in lectura.filas:
        if fila.saldo is None:
            anterior = None
            continue
        if anterior is not None:
            # el extracto puede venir en orden ascendente o descendente
            if fila.saldo != anterior.saldo + fila.importe and anterior.saldo != fila.saldo + anterior.importe:
                lectura.aviso(fila.numero, "El saldo no cuadra con la fila anterior: revisa que no falte ninguna.")
        anterior = fila
