"""Una contraseña débil (módulo 88): todos sus motivos."""

from usuarios.domain.exceptions.contrasena_no_valida_exception import ContrasenaNoValidaException


def test_una_contrasena_debil_da_todos_sus_motivos():
    e = ContrasenaNoValidaException(["Muy corta.", "Demasiado común."])
    assert (e.campo, e.mensajes) == ("password", ["Muy corta.", "Demasiado común."])
