"""Las formas de entrar de una cuenta (módulo 92), sin base de datos."""

import pytest

from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.ultimo_metodo_de_acceso_exception import UltimoMetodoDeAccesoException
from usuarios.domain.vo.metodos_de_acceso import MetodosDeAcceso


def test_una_passkey_tambien_es_una_forma_de_entrar():
    solo_google_y_passkey = MetodosDeAcceso(contrasena=False, proveedores=frozenset({Proveedor.GOOGLE}), passkeys=1)
    solo_google_y_passkey.sin(Proveedor.GOOGLE)  # queda la passkey
    with pytest.raises(UltimoMetodoDeAccesoException):
        solo_google_y_passkey.sin(Proveedor.GOOGLE).sin_una_passkey()
    MetodosDeAcceso(contrasena=True, proveedores=frozenset(), passkeys=1).sin_una_passkey()
