"""El estado de una cuenta (módulo 88), sin base de datos."""

from usuarios.domain.enums.estado_cuenta import EstadoCuenta


def test_el_estado_de_una_cuenta():
    assert EstadoCuenta.de(activa=False, con_contrasena=False) is EstadoCuenta.PENDIENTE  # sin completar el registro
    assert EstadoCuenta.de(activa=True, con_contrasena=True) is EstadoCuenta.ACTIVA
    assert EstadoCuenta.de(activa=True, con_contrasena=False) is EstadoCuenta.ACTIVA
    assert EstadoCuenta.de(activa=False, con_contrasena=True) is EstadoCuenta.DESACTIVADA  # por soporte
