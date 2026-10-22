"""SubirTicketUseCase con los fakes (módulo 88)."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from tickets.application.subir_ticket_use_case.dtos.subir_ticket_input_dto import SubirTicketInputDTO
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.domain.events.ticket_pendiente_event import TicketPendienteEvent
from tickets.domain.exceptions.cuenta_no_encontrada_exception import CuentaNoEncontradaException
from tickets.tests.fakes.mundo import HOGAR, Mundo, actor

E = EstadoTicket


def subir(mundo, rol=Rol.MIEMBRO, cuenta_id=10, huella="h1"):
    entrada = SubirTicketInputDTO(HOGAR, actor(rol), cuenta_id, b"jpeg", "foto.jpg", "image/jpeg", huella)
    return mundo.subir.ejecutar(entrada)


def test_subir_guarda_y_pide_procesarlo():
    mundo = Mundo()
    t = subir(mundo)
    assert (t.estado, t.subido_por_id, t.archivo) == (E.PENDIENTE, 7, f"tickets/{HOGAR}/{t.id}.jpg")
    assert mundo.eventos.publicados == [TicketPendienteEvent(t.id)]  # la tarea, al confirmar la transacción
    with pytest.raises(CuentaNoEncontradaException):
        subir(mundo, cuenta_id=20, huella="h2")  # la 20 es de otro hogar
    with pytest.raises(SinPermisoException):
        subir(mundo, rol=Rol.LECTOR, huella="h3")
