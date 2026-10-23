"""El step-up (módulo 92)."""

import pytest

from usuarios.application.reautenticar_use_case.dtos.reautenticar_input_dto import ReautenticarInputDTO
from usuarios.application.shared.dtos.autenticacion_output_dto import AutenticacionOutputDTO
from usuarios.domain.enums.factor import Factor
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.domain.exceptions.contrasena_incorrecta_exception import ContrasenaIncorrectaException
from usuarios.domain.exceptions.sesion_cerrada_exception import SesionCerradaException
from usuarios.tests.application.escenarios_mfa import con_mfa, entrar, segundo
from usuarios.tests.fakes.mundo import Mundo


def test_reautenticar_con_mfa_exige_un_segundo_factor():
    mundo = Mundo()
    ana = con_mfa(mundo)
    sesion, _ = segundo(mundo, entrar(mundo, ana).clave)
    with pytest.raises(CodigoNoValidoException):  # la contraseña sola no sube el nivel de una sesión que entró con dos
        mundo.reautenticar.ejecutar(ReautenticarInputDTO(ana, sesion.sid, Factor.CONTRASENA, "clave-larga-123"))
    mundo.segundos.guardados[ana].ultimo_paso -= 2
    nueva = mundo.reautenticar.ejecutar(ReautenticarInputDTO(ana, sesion.sid, Factor.TOTP, mundo.totp.ahora()))
    assert (
        AutenticacionOutputDTO.desde_vo(mundo.sesiones.autenticacion(sesion.sid)) == nueva
        and nueva.momento > sesion.autenticacion.momento
    )


def test_reautenticar_sin_mfa_con_la_contrasena_y_los_fallos_cuentan():
    mundo = Mundo()
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    sesion = entrar(mundo, luis)
    with pytest.raises(ContrasenaIncorrectaException):
        mundo.reautenticar.ejecutar(ReautenticarInputDTO(luis, sesion.sid, Factor.CONTRASENA, "mala"))
    assert mundo.segundos.guardados[luis].fallos == 1  # el fallo se guarda aunque el use case lance
    mundo.reautenticar.ejecutar(ReautenticarInputDTO(luis, sesion.sid, Factor.CONTRASENA, "clave-larga-123"))
    mundo.sesiones.cerrar(luis, sesion.sid)
    with pytest.raises(SesionCerradaException):
        mundo.reautenticar.ejecutar(ReautenticarInputDTO(luis, sesion.sid, Factor.CONTRASENA, "clave-larga-123"))
