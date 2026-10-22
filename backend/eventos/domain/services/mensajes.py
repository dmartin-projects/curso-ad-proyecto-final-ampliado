# eventos/domain/services/mensajes.py — el contrato de los mensajes que salen hacia Kafka (módulos 85 y 88)
#
# Qué viaja y qué no (privacidad: ni concepto ni notas), con qué clave y qué significa un valor nulo (tombstone). Es
# lo que el servicio de estadísticas (módulo 85, y su estructura hexagonal en el 89) espera recibir: un contrato entre
# dos sistemas, y por eso es dominio. Cómo se guarda (outbox) y cómo se publica (Kafka) es infraestructura.
from eventos.domain.vo.mensaje import Mensaje

MOVIMIENTOS = "gastos.movimientos"
MEMBRESIAS = "gastos.membresias"
ESQUEMA = "1"  # versión del formato de los mensajes; viaja en la cabecera "esquema"


# ── Movimientos ──
def datos_movimiento(m) -> dict:
    """Lo que viaja de un movimiento: lo justo para las estadísticas. Ni concepto ni notas (privacidad).

    `m` puede ser el modelo de Django o el BO del dominio (módulo 87): los dos tienen estos atributos.
    """
    return {
        "id": m.id,
        "hogar_id": m.hogar_id,
        "cuenta_id": m.cuenta_id,
        "fecha": str(m.fecha),  # date o "2026-10-21"
        "importe": str(m.importe),  # Decimal o Dinero, como texto ("-12.50"): un float perdería céntimos
        "categoria_id": m.categoria_id,
        "comercio_id": m.comercio_id,
        "origen": str(m.origen),
        "revisado": m.revisado,
    }


def movimiento(m, tipo: str) -> Mensaje:
    return Mensaje(MOVIMIENTOS, str(m.id), tipo, datos_movimiento(m))


def movimiento_eliminado(movimiento_id: int) -> Mensaje:
    return Mensaje(MOVIMIENTOS, str(movimiento_id), "movimiento.eliminado", None)


# ── Membresías: quién puede ver las estadísticas de qué hogar ──
def _clave_membresia(hogar_id: int, usuario_id: int) -> str:
    return f"{hogar_id}:{usuario_id}"


def membresia(hogar_id: int, usuario_id: int, rol: str, tipo: str = "membresia.guardada") -> Mensaje:
    valor = {"hogar_id": hogar_id, "usuario_id": usuario_id, "rol": str(rol)}
    return Mensaje(MEMBRESIAS, _clave_membresia(hogar_id, usuario_id), tipo, valor)


def membresia_eliminada(hogar_id: int, usuario_id: int) -> Mensaje:
    return Mensaje(MEMBRESIAS, _clave_membresia(hogar_id, usuario_id), "membresia.eliminada", None)
