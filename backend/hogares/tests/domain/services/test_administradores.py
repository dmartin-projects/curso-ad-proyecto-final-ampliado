"""La regla del último administrador (módulo 88), sin base de datos."""

import pytest

from core.domain.enums.rol import Rol
from hogares.domain.bo.membresia import Membresia
from hogares.domain.exceptions.ultimo_administrador_exception import UltimoAdministradorException
from hogares.domain.services.administradores import exigir_otro_admin


def test_el_ultimo_administrador_no_puede_irse_ni_dejar_de_serlo():
    admin = Membresia(hogar_id=1, usuario_id=1, rol=Rol.ADMIN)
    with pytest.raises(UltimoAdministradorException):
        exigir_otro_admin(admin, admins=1)
    exigir_otro_admin(admin, admins=2)
    exigir_otro_admin(Membresia(hogar_id=1, usuario_id=2, rol=Rol.LECTOR), admins=1)  # un lector sí puede irse
