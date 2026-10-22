"""El value object Actor y los roles (módulo 87)."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.actor import Actor


def test_actor_y_roles():
    Actor(1, Rol.ADMIN).exigir(Rol.MIEMBRO)
    with pytest.raises(SinPermisoException):
        Actor(1, Rol.LECTOR).exigir(Rol.MIEMBRO)
    assert Actor.sistema().rol == Rol.ADMIN and Actor.sistema().usuario_id is None
