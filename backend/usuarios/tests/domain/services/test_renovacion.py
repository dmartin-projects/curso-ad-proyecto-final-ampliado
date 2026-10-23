"""Un refresh que no es el vigente (módulo 92), sin base de datos."""

from datetime import timedelta

from usuarios.domain.enums.estado_renovacion import EstadoRenovacion
from usuarios.domain.services.renovacion import clasificar_refresh


def test_un_refresh_que_no_es_el_vigente():
    reciente, tarde = timedelta(seconds=3), timedelta(minutes=5)
    assert clasificar_refresh(presentado="a", anterior="a", desde_la_rotacion=reciente) is EstadoRenovacion.CONCURRENTE
    assert clasificar_refresh(presentado="a", anterior="a", desde_la_rotacion=tarde) is EstadoRenovacion.REUTILIZADA
    assert clasificar_refresh(presentado="z", anterior="a", desde_la_rotacion=reciente) is EstadoRenovacion.REUTILIZADA
    assert clasificar_refresh(presentado="", anterior="", desde_la_rotacion=reciente) is EstadoRenovacion.REUTILIZADA
