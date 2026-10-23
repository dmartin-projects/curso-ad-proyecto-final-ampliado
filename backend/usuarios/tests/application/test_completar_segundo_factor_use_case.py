"""El segundo paso del login: códigos, intentos, bloqueos y passkeys como segundo factor (módulo 92)."""

import pytest

from usuarios.application.confirmar_recuperacion_use_case.dtos.confirmar_recuperacion_input_dto import (
    ConfirmarRecuperacionInputDTO,
)
from usuarios.application.pedir_reto_use_case.dtos.pedir_reto_input_dto import PedirRetoInputDTO
from usuarios.application.shared.dtos.segundo_factor_pendiente_output_dto import SegundoFactorPendienteOutputDTO
from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.factor import Factor
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent
from usuarios.domain.exceptions.codigo_no_valido_exception import CodigoNoValidoException
from usuarios.domain.exceptions.login_pendiente_no_valido_exception import LoginPendienteNoValidoException
from usuarios.domain.exceptions.passkey_no_valida_exception import PasskeyNoValidaException
from usuarios.domain.exceptions.segundo_factor_bloqueado_exception import SegundoFactorBloqueadoException
from usuarios.domain.exceptions.segundo_factor_bloqueado_hasta_recuperar_exception import (
    SegundoFactorBloqueadoHastaRecuperarException,
)
from usuarios.tests.application.escenarios_mfa import con_mfa, entrar, firma, registrar_passkey, segundo
from usuarios.tests.fakes.mundo import Mundo


def test_con_mfa_la_contrasena_no_abre_la_sesion_sino_el_segundo_paso():
    mundo = Mundo()
    ana = con_mfa(mundo)
    pendiente = entrar(mundo, ana)
    assert isinstance(pendiente, SegundoFactorPendienteOutputDTO) and not mundo.sesiones.filas  # ni sesión ni tokens
    assert pendiente.factores == ["totp", "recuperacion"]  # lo que puede ofrecer la pantalla del segundo paso
    sesion, _ = segundo(mundo, pendiente.clave)
    assert sesion.tokens.access.startswith(f"access-{ana}-")
    assert sesion.autenticacion.amr == ["mfa", "otp", "pwd"]


def test_con_un_proveedor_tambien_hace_falta_el_segundo_factor():
    mundo = Mundo()
    ana = con_mfa(mundo)
    pendiente = entrar(mundo, ana, Factor.PROVEEDOR)
    assert isinstance(pendiente, SegundoFactorPendienteOutputDTO)
    assert segundo(mundo, pendiente.clave)[0].autenticacion.amr == ["fed", "mfa", "otp"]


def test_el_mismo_codigo_no_vale_dos_veces():
    mundo = Mundo()
    ana = con_mfa(mundo)
    codigo = mundo.totp.ahora()
    segundo(mundo, entrar(mundo, ana).clave, codigo=codigo)
    with pytest.raises(CodigoNoValidoException):  # quien lo vio por encima del hombro, un segundo después
        segundo(mundo, entrar(mundo, ana).clave, codigo=codigo)


def test_un_codigo_de_recuperacion_vale_una_vez():
    mundo = Mundo()
    ana = con_mfa(mundo)
    codigo = mundo.codigos_de_ana[0]
    sesion, _ = segundo(mundo, entrar(mundo, ana).clave, Factor.RECUPERACION, codigo)
    assert sesion.autenticacion.factores == {Factor.CONTRASENA, Factor.RECUPERACION}
    with pytest.raises(CodigoNoValidoException):
        segundo(mundo, entrar(mundo, ana).clave, Factor.RECUPERACION, codigo)
    assert mundo.codigos.quedan(ana) == 9


def test_cinco_intentos_por_login_y_vuelta_a_la_contrasena():
    mundo = Mundo()
    ana = con_mfa(mundo)
    clave = entrar(mundo, ana).clave
    for _ in range(5):
        with pytest.raises(CodigoNoValidoException):
            segundo(mundo, clave, codigo="000000")
    with pytest.raises(LoginPendienteNoValidoException):  # ni con el bueno: ese login a medias ya no existe
        segundo(mundo, clave)


def test_los_fallos_bloquean_la_cuenta_aunque_se_empiece_de_nuevo():
    """El límite por login no basta (se vuelve a poner la contraseña y otros 5): el de verdad es el de la cuenta, y
    el fallo queda guardado aunque el use case lance la excepción."""
    mundo = Mundo()
    ana = con_mfa(mundo)
    for _ in range(5):
        with pytest.raises(CodigoNoValidoException):
            segundo(mundo, entrar(mundo, ana).clave, codigo="000000")
    assert mundo.segundos.guardados[ana].fallos == 5
    with pytest.raises(SegundoFactorBloqueadoException):
        segundo(mundo, entrar(mundo, ana).clave)  # ni con el bueno, durante un minuto
    assert ana in mundo.segundos.bloqueos  # la fila, bloqueada mientras se decide (dos intentos a la vez)
    # y a los 5 fallos seguidos, un aviso: quien prueba códigos ya tiene la contraseña
    assert mundo.eventos.de_tipo(SeguridadCambiadaEvent)[-1] == SeguridadCambiadaEvent(ana, "fallos_segundo_factor")


def test_el_techo_de_fallos_bloquea_hasta_recuperar_la_cuenta():
    mundo = Mundo()
    ana = con_mfa(mundo)
    mundo.segundos.guardados[ana].fallos = 99  # p. ej., tras días de intentos, esperando cada bloqueo
    with pytest.raises(CodigoNoValidoException):
        segundo(mundo, entrar(mundo, ana).clave, codigo="000000")  # el fallo 100
    assert SeguridadCambiadaEvent(ana, "segundo_factor_bloqueado") in mundo.eventos.publicados
    with pytest.raises(SegundoFactorBloqueadoHastaRecuperarException):
        segundo(mundo, entrar(mundo, ana).clave)  # ni con el bueno
    sesion = entrar(mundo, mundo.cuentas.crear_verificada(email="b@example.com", nombre="B", apellidos=""))
    mundo.confirmar.ejecutar(
        ConfirmarRecuperacionInputDTO(str(ana), "ok", "otra-clave-muy-larga")
    )  # el enlace del email: la cuenta es suya
    assert mundo.segundos.guardados[ana].fallos == 0
    assert segundo(mundo, entrar(mundo, ana).clave)[0].autenticacion.multifactor
    assert mundo.sesiones.autenticacion(sesion.sid) is not None  # (las sesiones de otra cuenta, intactas)


def test_si_el_fallo_no_se_puede_guardar_cuenta_como_bloqueo():
    """Fail closed: si algo inesperado impide anotar el fallo, el intento se trata como un bloqueo (y el del login
    pendiente ya estaba gastado), no como un error que se puede repetir sin que nada cuente."""
    mundo = Mundo()
    ana = con_mfa(mundo)
    clave = entrar(mundo, ana).clave

    def roto(segundo):
        raise RuntimeError("la base de datos no responde")

    mundo.segundos.guardar = roto
    for _ in range(5):
        with pytest.raises(SegundoFactorBloqueadoException):
            segundo(mundo, clave, codigo="000000")
    with pytest.raises(LoginPendienteNoValidoException):  # los 5 intentos del login pendiente, gastados igualmente
        segundo(mundo, clave)


def test_el_login_pendiente_vale_una_vez():
    mundo = Mundo()
    ana = con_mfa(mundo)
    clave = entrar(mundo, ana).clave
    segundo(mundo, clave, Factor.RECUPERACION, mundo.codigos_de_ana[0])
    with pytest.raises(LoginPendienteNoValidoException):  # la misma cookie, otra vez: no abre otra sesión
        segundo(mundo, clave, Factor.RECUPERACION, mundo.codigos_de_ana[1])


def test_el_login_pendiente_es_del_canal_donde_empezo():
    mundo = Mundo()
    ana = con_mfa(mundo)
    clave = entrar(mundo, ana).clave  # en la SPA
    with pytest.raises(LoginPendienteNoValidoException):
        segundo(mundo, clave, canal=Canal.AUTORIZACION)
    assert segundo(mundo, clave)[0].tokens is not None


def test_una_passkey_como_segundo_factor():
    mundo = Mundo()
    ana = con_mfa(mundo)
    registrar_passkey(mundo, ana)
    clave = entrar(mundo, ana).clave
    opciones = mundo.pedir_reto.ejecutar(PedirRetoInputDTO(f"segundo:{clave}", ana))
    assert mundo.webauthn.pedidos[-1] == {"permitir": [b"cred-1"], "uv": False}  # solo las suyas
    sesion, _ = segundo(mundo, clave, Factor.PASSKEY, "", respuesta=firma(mundo, opciones, uv=False, usuario_id=ana))
    assert Factor.PASSKEY in sesion.autenticacion.factores


def test_la_passkey_de_otra_cuenta_no_sirve_de_segundo_factor():
    mundo = Mundo()
    ana = con_mfa(mundo)
    luis = mundo.cuentas.crear_pendiente(email="luis@example.com", nombre="Luis", apellidos="")
    mundo.cuentas.completar_registro(luis, "clave-larga-123")
    registrar_passkey(mundo, luis, "cred-luis")
    clave = entrar(mundo, ana).clave
    opciones = mundo.pedir_reto.ejecutar(PedirRetoInputDTO(f"segundo:{clave}", ana))
    with pytest.raises(PasskeyNoValidaException):
        segundo(mundo, clave, Factor.PASSKEY, "", respuesta=firma(mundo, opciones, "cred-luis", usuario_id=luis))
