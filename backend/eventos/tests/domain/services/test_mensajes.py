"""El contrato de los mensajes hacia Kafka (módulos 85 y 88): qué viaja y qué no, sin base de datos."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from core.domain.vo.dinero import Dinero
from eventos.domain.services import mensajes
from eventos.domain.vo.mensaje import Mensaje


def test_un_movimiento_viaja_sin_concepto_ni_notas_y_con_el_importe_como_texto():
    m = SimpleNamespace(id=7, hogar_id=1, cuenta_id=2, fecha=date(2026, 10, 1), importe=Dinero("-12.5"),
                        categoria_id=None, comercio_id=3, origen="ticket", revisado=False,
                        concepto="Farmacia Pérez", notas="la receta de Ana")  # fmt: skip
    msg = mensajes.movimiento(m, "movimiento.creado")
    assert (msg.topic, msg.clave, msg.tipo) == (mensajes.MOVIMIENTOS, "7", "movimiento.creado")
    assert msg.valor == {"id": 7, "hogar_id": 1, "cuenta_id": 2, "fecha": "2026-10-01", "importe": "-12.50",
                         "categoria_id": None, "comercio_id": 3, "origen": "ticket", "revisado": False}  # fmt: skip
    assert "Farmacia" not in str(msg.valor) and "receta" not in str(msg.valor)
    assert mensajes.datos_movimiento(SimpleNamespace(**vars(m) | {"importe": Decimal("-12.50")})) == msg.valor


def test_tombstones_y_membresias_con_la_misma_clave():
    assert mensajes.movimiento_eliminado(7) == Mensaje(mensajes.MOVIMIENTOS, "7", "movimiento.eliminado", None)
    guardada, borrada = mensajes.membresia(3, 9, "lector"), mensajes.membresia_eliminada(3, 9)
    assert guardada.clave == borrada.clave == "3:9"  # misma clave → misma partición → el borrado llega después
    assert guardada.valor == {"hogar_id": 3, "usuario_id": 9, "rol": "lector"} and borrada.valor is None
