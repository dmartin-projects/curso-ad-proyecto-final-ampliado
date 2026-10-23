"""Ana con el MFA activo, sus inicios de sesión y sus passkeys, con los fakes del Mundo (módulo 92)."""

from usuarios.application.completar_segundo_factor_use_case.dtos.completar_segundo_factor_input_dto import (
    CompletarSegundoFactorInputDTO,
)
from usuarios.application.confirmar_totp_use_case.dtos.confirmar_totp_input_dto import ConfirmarTotpInputDTO
from usuarios.application.empezar_registro_passkey_use_case.dtos.empezar_registro_passkey_input_dto import (
    EmpezarRegistroPasskeyInputDTO,
)
from usuarios.application.empezar_totp_use_case.dtos.empezar_totp_input_dto import EmpezarTotpInputDTO
from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.application.registrar_passkey_use_case.dtos.registrar_passkey_input_dto import RegistrarPasskeyInputDTO
from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.factor import Factor
from usuarios.domain.vo.contexto import Contexto
from usuarios.tests.fakes.mundo import Mundo

CHROME = Contexto("Mozilla/5.0 (Macintosh; Intel Mac OS X) Chrome/141.0", "83.45.120.17", "cookie-del-portatil")


def con_mfa(mundo: Mundo) -> int:
    """Ana, con contraseña y el MFA activo (TOTP confirmado y sus códigos de recuperación)."""
    usuario_id = mundo.cuentas.crear_pendiente(email="ana@example.com", nombre="Ana", apellidos="")
    mundo.cuentas.completar_registro(usuario_id, "clave-larga-123")
    mundo.empezar_totp.ejecutar(EmpezarTotpInputDTO(usuario_id, "ana@example.com"))
    mundo.codigos_de_ana = mundo.confirmar_totp.ejecutar(ConfirmarTotpInputDTO(usuario_id, mundo.totp.ahora()))
    mundo.segundos.guardados[usuario_id].ultimo_paso -= 2  # (que el código de ahora se pueda usar en el test)
    return usuario_id


def entrar(mundo, usuario_id, factor=Factor.CONTRASENA, canal=Canal.SPA, contexto=CHROME):
    return mundo.iniciar_sesion.ejecutar(IniciarSesionInputDTO(usuario_id, factor, canal, contexto))


def segundo(mundo, clave, factor=Factor.TOTP, codigo=None, canal=Canal.SPA, **extra):
    codigo = mundo.totp.ahora() if codigo is None else codigo
    return mundo.segundo_paso.ejecutar(
        CompletarSegundoFactorInputDTO(clave, canal, factor, codigo, contexto=CHROME, **extra)
    )


def registrar_passkey(mundo, usuario_id, credencial="cred-1", sincronizada=False):
    opciones = mundo.empezar_registro.ejecutar(EmpezarRegistroPasskeyInputDTO(usuario_id, "ana@example.com", "Ana"))
    respuesta = {"id": credencial, "challenge": opciones["challenge"], "sincronizada": sincronizada}
    return mundo.registrar_passkey.ejecutar(RegistrarPasskeyInputDTO(usuario_id, "Portátil", respuesta))


def firma(mundo, opciones, credencial="cred-1", contador=1, uv=True, manija=None, usuario_id=1):
    return {"id": credencial, "challenge": opciones["challenge"], "firma": "buena", "contador": contador, "uv": uv,
            "manija": manija if manija is not None else mundo.passkeys.manija(usuario_id)}  # fmt: skip


def reautenticar_con_google(mundo, usuario_id, sid, **perfil):
    from dataclasses import replace

    from usuarios.application.completar_login_social_use_case.dtos.completar_login_social_input_dto import (
        CompletarLoginSocialInputDTO,
    )
    from usuarios.application.empezar_login_social_use_case.dtos.empezar_login_social_input_dto import (
        EmpezarLoginSocialInputDTO,
    )
    from usuarios.domain.enums.proposito import Proposito
    from usuarios.domain.enums.proveedor import Proveedor

    cmd = EmpezarLoginSocialInputDTO(Proveedor.GOOGLE, Proposito.REAUTENTICAR, "/seguridad", usuario_id, sid)
    ida = mundo.empezar.ejecutar(cmd)
    transaccion = mundo.google.transacciones[-1]
    mundo.google.perfil = replace(mundo.google.perfil, **({"autenticado_en": transaccion.desde} | perfil))
    parametros = {"state": transaccion.state, "code": "c"}
    return mundo.completar.ejecutar(CompletarLoginSocialInputDTO(Proveedor.GOOGLE, ida.clave, parametros))


def cuenta_de_google(mundo):
    from usuarios.domain.enums.proveedor import Proveedor
    from usuarios.domain.vo.perfil_externo import PerfilExterno

    ana = mundo.cuentas.crear_verificada(email="ana@gmail.com", nombre="Ana", apellidos="")
    mundo.identidades.vincular(ana, PerfilExterno(Proveedor.GOOGLE, "sub-ana", "ana@gmail.com", True))
    sesion = entrar(mundo, ana, Factor.PROVEEDOR)
    return ana, sesion.sid
