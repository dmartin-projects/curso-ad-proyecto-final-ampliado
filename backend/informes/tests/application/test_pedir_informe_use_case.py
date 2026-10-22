"""PedirInformeUseCase con fakes (módulo 88)."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.actor import Actor
from core.domain.vo.mes import Mes
from informes.application.pedir_informe_use_case.dtos.pedir_informe_input_dto import PedirInformeInputDTO
from informes.domain.events.informe_pedido_event import InformePedidoEvent
from informes.domain.exceptions.mes_futuro_exception import MesFuturoException

OCT = Mes(2026, 10)


def actor(rol: Rol = Rol.MIEMBRO, usuario_id: int = 7) -> Actor:
    return Actor(usuario_id=usuario_id, rol=rol)


def test_pedir_exige_miembro_y_mes_no_futuro(mundo):
    pedir, _, _, eventos = mundo
    assert pedir.ejecutar(PedirInformeInputDTO(1, actor(), OCT, enviar=True)) == OCT
    assert eventos.publicados == [InformePedidoEvent(1, OCT, 7, True)]
    with pytest.raises(MesFuturoException):
        pedir.ejecutar(PedirInformeInputDTO(1, actor(), Mes(2026, 11)))
    with pytest.raises(SinPermisoException):
        pedir.ejecutar(PedirInformeInputDTO(1, actor(Rol.LECTOR), OCT))
