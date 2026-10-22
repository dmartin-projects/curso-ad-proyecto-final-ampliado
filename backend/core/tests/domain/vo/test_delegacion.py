"""Actor.limitado_a y Delegacion (módulos 87 y 90), sin base de datos."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.vo.actor import Actor
from core.domain.vo.delegacion import Delegacion


@pytest.mark.parametrize(
    "rol, techo, efectivo",
    [
        (Rol.ADMIN, Rol.MIEMBRO, Rol.MIEMBRO),  # el scope limita
        (Rol.ADMIN, Rol.LECTOR, Rol.LECTOR),
        (Rol.LECTOR, Rol.MIEMBRO, Rol.LECTOR),  # el rol limita: un scope no da permisos
        (Rol.MIEMBRO, Rol.MIEMBRO, Rol.MIEMBRO),
    ],
)
def test_una_aplicacion_puede_la_interseccion_del_rol_y_sus_scopes(rol, techo, efectivo):
    assert Actor(7, rol).limitado_a(techo) == Actor(7, efectivo)


def test_sin_techo_no_puede_nada():
    with pytest.raises(SinPermisoException):
        Actor(7, Rol.ADMIN).limitado_a(None)


def test_el_actor_limitado_no_pasa_lo_que_su_rol_si():
    Actor(7, Rol.ADMIN).exigir(Rol.ADMIN)
    with pytest.raises(SinPermisoException):
        Actor(7, Rol.ADMIN).limitado_a(Rol.MIEMBRO).exigir(Rol.ADMIN)


def test_delegacion():
    d = Delegacion("gastos-cli", frozenset({"openid", "gastos:leer"}), Rol.LECTOR)
    assert d.permite("gastos:leer") and not d.permite("gastos:escribir")
