# usuarios/infrastructure/container.py — composition root de las cuentas (módulos 88, 91 y 92)
from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from usuarios.application.borrar_passkey_use_case.borrar_passkey_use_case import BorrarPasskeyUseCase
from usuarios.application.borrar_passkey_use_case.i_borrar_passkey_use_case import IBorrarPasskeyUseCase
from usuarios.application.cambiar_contrasena_use_case.cambiar_contrasena_use_case import CambiarContrasenaUseCase
from usuarios.application.cambiar_contrasena_use_case.i_cambiar_contrasena_use_case import ICambiarContrasenaUseCase
from usuarios.application.cerrar_las_demas_use_case.cerrar_las_demas_use_case import CerrarLasDemasUseCase
from usuarios.application.cerrar_las_demas_use_case.i_cerrar_las_demas_use_case import ICerrarLasDemasUseCase
from usuarios.application.cerrar_sesion_use_case.cerrar_sesion_use_case import CerrarSesionUseCase
from usuarios.application.cerrar_sesion_use_case.i_cerrar_sesion_use_case import ICerrarSesionUseCase
from usuarios.application.completar_login_social_use_case.completar_login_social_use_case import (
    CompletarLoginSocialUseCase,
)
from usuarios.application.completar_login_social_use_case.i_completar_login_social_use_case import (
    ICompletarLoginSocialUseCase,
)
from usuarios.application.completar_registro_use_case.completar_registro_use_case import CompletarRegistroUseCase
from usuarios.application.completar_registro_use_case.i_completar_registro_use_case import ICompletarRegistroUseCase
from usuarios.application.completar_segundo_factor_use_case.completar_segundo_factor_use_case import (
    CompletarSegundoFactorUseCase,
)
from usuarios.application.completar_segundo_factor_use_case.i_completar_segundo_factor_use_case import (
    ICompletarSegundoFactorUseCase,
)
from usuarios.application.comprobar_autenticacion_reciente_use_case.comprobar_autenticacion_reciente_use_case import (
    ComprobarAutenticacionRecienteUseCase,
)
from usuarios.application.comprobar_autenticacion_reciente_use_case.i_comprobar_autenticacion_reciente_use_case import (
    IComprobarAutenticacionRecienteUseCase,
)
from usuarios.application.confirmar_recuperacion_use_case.confirmar_recuperacion_use_case import (
    ConfirmarRecuperacionUseCase,
)
from usuarios.application.confirmar_recuperacion_use_case.i_confirmar_recuperacion_use_case import (
    IConfirmarRecuperacionUseCase,
)
from usuarios.application.confirmar_totp_use_case.confirmar_totp_use_case import ConfirmarTotpUseCase
from usuarios.application.confirmar_totp_use_case.i_confirmar_totp_use_case import IConfirmarTotpUseCase
from usuarios.application.desactivar_mfa_use_case.desactivar_mfa_use_case import DesactivarMfaUseCase
from usuarios.application.desactivar_mfa_use_case.i_desactivar_mfa_use_case import IDesactivarMfaUseCase
from usuarios.application.desvincular_use_case.desvincular_use_case import DesvincularUseCase
from usuarios.application.desvincular_use_case.i_desvincular_use_case import IDesvincularUseCase
from usuarios.application.empezar_login_social_use_case.empezar_login_social_use_case import EmpezarLoginSocialUseCase
from usuarios.application.empezar_login_social_use_case.i_empezar_login_social_use_case import (
    IEmpezarLoginSocialUseCase,
)
from usuarios.application.empezar_registro_passkey_use_case.empezar_registro_passkey_use_case import (
    EmpezarRegistroPasskeyUseCase,
)
from usuarios.application.empezar_registro_passkey_use_case.i_empezar_registro_passkey_use_case import (
    IEmpezarRegistroPasskeyUseCase,
)
from usuarios.application.empezar_totp_use_case.empezar_totp_use_case import EmpezarTotpUseCase
from usuarios.application.empezar_totp_use_case.i_empezar_totp_use_case import IEmpezarTotpUseCase
from usuarios.application.entrar_con_passkey_use_case.entrar_con_passkey_use_case import EntrarConPasskeyUseCase
from usuarios.application.entrar_con_passkey_use_case.i_entrar_con_passkey_use_case import IEntrarConPasskeyUseCase
from usuarios.application.establecer_contrasena_use_case.establecer_contrasena_use_case import (
    EstablecerContrasenaUseCase,
)
from usuarios.application.establecer_contrasena_use_case.i_establecer_contrasena_use_case import (
    IEstablecerContrasenaUseCase,
)
from usuarios.application.iniciar_sesion_use_case.i_iniciar_sesion_use_case import IIniciarSesionUseCase
from usuarios.application.iniciar_sesion_use_case.iniciar_sesion_use_case import IniciarSesionUseCase
from usuarios.application.listar_proveedores_use_case.i_listar_proveedores_use_case import IListarProveedoresUseCase
from usuarios.application.listar_proveedores_use_case.listar_proveedores_use_case import ListarProveedoresUseCase
from usuarios.application.listar_sesiones_use_case.i_listar_sesiones_use_case import IListarSesionesUseCase
from usuarios.application.listar_sesiones_use_case.listar_sesiones_use_case import ListarSesionesUseCase
from usuarios.application.obtener_acceso_use_case.i_obtener_acceso_use_case import IObtenerAccesoUseCase
from usuarios.application.obtener_acceso_use_case.obtener_acceso_use_case import ObtenerAccesoUseCase
from usuarios.application.obtener_autenticacion_use_case.i_obtener_autenticacion_use_case import (
    IObtenerAutenticacionUseCase,
)
from usuarios.application.obtener_autenticacion_use_case.obtener_autenticacion_use_case import (
    ObtenerAutenticacionUseCase,
)
from usuarios.application.obtener_factores_use_case.i_obtener_factores_use_case import IObtenerFactoresUseCase
from usuarios.application.obtener_factores_use_case.obtener_factores_use_case import ObtenerFactoresUseCase
from usuarios.application.obtener_login_pendiente_use_case.i_obtener_login_pendiente_use_case import (
    IObtenerLoginPendienteUseCase,
)
from usuarios.application.obtener_login_pendiente_use_case.obtener_login_pendiente_use_case import (
    ObtenerLoginPendienteUseCase,
)
from usuarios.application.obtener_seguridad_use_case.i_obtener_seguridad_use_case import IObtenerSeguridadUseCase
from usuarios.application.obtener_seguridad_use_case.obtener_seguridad_use_case import ObtenerSeguridadUseCase
from usuarios.application.pedir_reto_use_case.i_pedir_reto_use_case import IPedirRetoUseCase
from usuarios.application.pedir_reto_use_case.pedir_reto_use_case import PedirRetoUseCase
from usuarios.application.reautenticar_use_case.i_reautenticar_use_case import IReautenticarUseCase
from usuarios.application.reautenticar_use_case.reautenticar_use_case import ReautenticarUseCase
from usuarios.application.registrar_passkey_use_case.i_registrar_passkey_use_case import IRegistrarPasskeyUseCase
from usuarios.application.registrar_passkey_use_case.registrar_passkey_use_case import RegistrarPasskeyUseCase
from usuarios.application.renovar_sesion_use_case.i_renovar_sesion_use_case import IRenovarSesionUseCase
from usuarios.application.renovar_sesion_use_case.renovar_sesion_use_case import RenovarSesionUseCase
from usuarios.application.shared.apertura_de_sesion import AperturaDeSesion
from usuarios.application.shared.comprobar_factor import ComprobarFactor
from usuarios.application.shared.factores_de_cuenta import FactoresDeCuenta
from usuarios.application.solicitar_recuperacion_use_case.i_solicitar_recuperacion_use_case import (
    ISolicitarRecuperacionUseCase,
)
from usuarios.application.solicitar_recuperacion_use_case.solicitar_recuperacion_use_case import (
    SolicitarRecuperacionUseCase,
)
from usuarios.application.solicitar_registro_use_case.i_solicitar_registro_use_case import ISolicitarRegistroUseCase
from usuarios.application.solicitar_registro_use_case.solicitar_registro_use_case import SolicitarRegistroUseCase
from usuarios.infrastructure.auth.enlaces_django import EnlacesDjango
from usuarios.infrastructure.auth.politica_de_contrasenas_django import PoliticaDeContrasenasDjango
from usuarios.infrastructure.auth.tokens_simple_jwt import TokensSimpleJWT
from usuarios.infrastructure.cache.pendientes_en_cache import PendientesEnCache
from usuarios.infrastructure.cache.retos_en_cache import RetosEnCache
from usuarios.infrastructure.cache.transacciones_en_cache import TransaccionesEnCache
from usuarios.infrastructure.database.repositories.acceso_query_service_orm import AccesoQueryServiceORM
from usuarios.infrastructure.database.repositories.cuenta_command_repository_orm import CuentaCommandRepositoryORM
from usuarios.infrastructure.database.repositories.identidad_command_repository_orm import (
    IdentidadCommandRepositoryORM,
)
from usuarios.infrastructure.database.repositories.passkey_command_repository_orm import PasskeyCommandRepositoryORM
from usuarios.infrastructure.database.repositories.segundo_factor_command_repository_orm import (
    SegundoFactorCommandRepositoryORM,
)
from usuarios.infrastructure.database.repositories.seguridad_query_service_orm import SeguridadQueryServiceORM
from usuarios.infrastructure.database.repositories.sesion_activa_query_service_orm import SesionActivaQueryServiceORM
from usuarios.infrastructure.database.services.codigos_de_recuperacion_orm import CodigosDeRecuperacionORM
from usuarios.infrastructure.database.services.sesiones_orm import SesionesORM
from usuarios.infrastructure.messaging.publicador_eventos_django import PublicadorEventosDjango
from usuarios.infrastructure.mfa.codigo_qr_segno import CodigoQrSegno
from usuarios.infrastructure.mfa.totp_pyotp import TotpPyotp
from usuarios.infrastructure.mfa.webauthn_duo import WebAuthnDuo
from usuarios.infrastructure.providers.proveedores_configurados import ProveedoresConfigurados


def solicitar_registro() -> ISolicitarRegistroUseCase:
    return SolicitarRegistroUseCase(
        cuentas=CuentaCommandRepositoryORM(),
        enlaces=EnlacesDjango(),
        eventos=PublicadorEventosDjango(),
        uow=UnidadDeTrabajoDjango(),
    )


def completar_registro() -> ICompletarRegistroUseCase:
    return CompletarRegistroUseCase(
        cuentas=CuentaCommandRepositoryORM(), politica=PoliticaDeContrasenasDjango(), enlaces=EnlacesDjango()
    )


def solicitar_recuperacion() -> ISolicitarRecuperacionUseCase:
    return SolicitarRecuperacionUseCase(
        cuentas=CuentaCommandRepositoryORM(),
        enlaces=EnlacesDjango(),
        eventos=PublicadorEventosDjango(),
        uow=UnidadDeTrabajoDjango(),
    )


def confirmar_recuperacion() -> IConfirmarRecuperacionUseCase:
    return ConfirmarRecuperacionUseCase(
        cuentas=CuentaCommandRepositoryORM(), politica=PoliticaDeContrasenasDjango(), enlaces=EnlacesDjango(),
        sesiones=SesionesORM(), segundos=SegundoFactorCommandRepositoryORM(), eventos=PublicadorEventosDjango(),
        uow=UnidadDeTrabajoDjango(),
    )  # fmt: skip


def cambiar_contrasena() -> ICambiarContrasenaUseCase:
    return CambiarContrasenaUseCase(
        cuentas=CuentaCommandRepositoryORM(),
        politica=PoliticaDeContrasenasDjango(),
        sesiones=SesionesORM(),
        uow=UnidadDeTrabajoDjango(),
    )


# ── Módulo 91: sesiones y social login ──


def iniciar_sesion() -> IIniciarSesionUseCase:
    return IniciarSesionUseCase(
        cuentas=CuentaCommandRepositoryORM(), segundos=SegundoFactorCommandRepositoryORM(),
        pendientes=PendientesEnCache(), factores=_factores(), apertura=_apertura(), reloj=RelojDjango(),
    )  # fmt: skip


def listar_proveedores() -> IListarProveedoresUseCase:
    return ListarProveedoresUseCase(proveedores=ProveedoresConfigurados())


def empezar_login_social() -> IEmpezarLoginSocialUseCase:
    return EmpezarLoginSocialUseCase(proveedores=ProveedoresConfigurados(), transacciones=TransaccionesEnCache())


def completar_login_social() -> ICompletarLoginSocialUseCase:
    return CompletarLoginSocialUseCase(
        proveedores=ProveedoresConfigurados(),
        transacciones=TransaccionesEnCache(),
        identidades=IdentidadCommandRepositoryORM(),
        cuentas=CuentaCommandRepositoryORM(),
        eventos=PublicadorEventosDjango(),  # ejercicio 2: el aviso al vincular
        uow=UnidadDeTrabajoDjango(),
    )


def desvincular() -> IDesvincularUseCase:
    return DesvincularUseCase(
        identidades=IdentidadCommandRepositoryORM(), cuentas=CuentaCommandRepositoryORM(),
        passkeys=PasskeyCommandRepositoryORM(), uow=UnidadDeTrabajoDjango(),
    )  # fmt: skip


def establecer_contrasena() -> IEstablecerContrasenaUseCase:
    return EstablecerContrasenaUseCase(cuentas=CuentaCommandRepositoryORM(), politica=PoliticaDeContrasenasDjango())


def obtener_acceso() -> IObtenerAccesoUseCase:
    return ObtenerAccesoUseCase(acceso=AccesoQueryServiceORM())


# ── Módulo 92: segundo factor, passkeys, step-up y sesiones ──


def _factores() -> FactoresDeCuenta:
    return FactoresDeCuenta(
        cuentas=CuentaCommandRepositoryORM(), segundos=SegundoFactorCommandRepositoryORM(),
        codigos=CodigosDeRecuperacionORM(), passkeys=PasskeyCommandRepositoryORM(),
    )  # fmt: skip


def _apertura() -> AperturaDeSesion:
    return AperturaDeSesion(
        sesiones=SesionesORM(), tokens=TokensSimpleJWT(), eventos=PublicadorEventosDjango(), uow=UnidadDeTrabajoDjango()
    )


def _comprobar() -> ComprobarFactor:
    return ComprobarFactor(
        cuentas=CuentaCommandRepositoryORM(), segundos=SegundoFactorCommandRepositoryORM(), totp=TotpPyotp(),
        codigos=CodigosDeRecuperacionORM(), passkeys=PasskeyCommandRepositoryORM(), webauthn=WebAuthnDuo(),
        retos=RetosEnCache(), eventos=PublicadorEventosDjango(), reloj=RelojDjango(),
    )  # fmt: skip


def completar_segundo_factor() -> ICompletarSegundoFactorUseCase:
    return CompletarSegundoFactorUseCase(
        apertura=_apertura(), comprobar=_comprobar(), pendientes=PendientesEnCache(), uow=UnidadDeTrabajoDjango(),
        reloj=RelojDjango(),
    )  # fmt: skip


def obtener_login_pendiente() -> IObtenerLoginPendienteUseCase:
    return ObtenerLoginPendienteUseCase(pendientes=PendientesEnCache())


def obtener_factores() -> IObtenerFactoresUseCase:
    return ObtenerFactoresUseCase(factores=_factores())


def reautenticar() -> IReautenticarUseCase:
    return ReautenticarUseCase(
        factores=_factores(), comprobar=_comprobar(), sesiones=SesionesORM(), uow=UnidadDeTrabajoDjango(),
        reloj=RelojDjango(),
    )  # fmt: skip


def obtener_autenticacion() -> IObtenerAutenticacionUseCase:
    """La autenticación de una sesión abierta (el authorization server: ¿sigue viva su sesión de Django?)."""
    return ObtenerAutenticacionUseCase(sesiones=SesionesORM())


def comprobar_autenticacion_reciente() -> IComprobarAutenticacionRecienteUseCase:
    return ComprobarAutenticacionRecienteUseCase(sesiones=SesionesORM(), reloj=RelojDjango())


def renovar_sesion() -> IRenovarSesionUseCase:
    return RenovarSesionUseCase(sesiones=SesionesORM(), eventos=PublicadorEventosDjango(), uow=UnidadDeTrabajoDjango())


def cerrar_sesion() -> ICerrarSesionUseCase:
    return CerrarSesionUseCase(sesiones=SesionesORM())


def cerrar_las_demas() -> ICerrarLasDemasUseCase:
    return CerrarLasDemasUseCase(sesiones=SesionesORM())


def listar_sesiones() -> IListarSesionesUseCase:
    return ListarSesionesUseCase(sesiones=SesionActivaQueryServiceORM())


def obtener_seguridad() -> IObtenerSeguridadUseCase:
    return ObtenerSeguridadUseCase(seguridad=SeguridadQueryServiceORM())


def empezar_totp() -> IEmpezarTotpUseCase:
    return EmpezarTotpUseCase(
        segundos=SegundoFactorCommandRepositoryORM(), totp=TotpPyotp(), qr=CodigoQrSegno(), uow=UnidadDeTrabajoDjango()
    )


def confirmar_totp() -> IConfirmarTotpUseCase:
    return ConfirmarTotpUseCase(
        segundos=SegundoFactorCommandRepositoryORM(), totp=TotpPyotp(), codigos=CodigosDeRecuperacionORM(),
        eventos=PublicadorEventosDjango(), uow=UnidadDeTrabajoDjango(), reloj=RelojDjango(),
    )  # fmt: skip


def desactivar_mfa() -> IDesactivarMfaUseCase:
    return DesactivarMfaUseCase(
        segundos=SegundoFactorCommandRepositoryORM(), codigos=CodigosDeRecuperacionORM(),
        eventos=PublicadorEventosDjango(), uow=UnidadDeTrabajoDjango(),
    )  # fmt: skip


def pedir_reto() -> IPedirRetoUseCase:
    return PedirRetoUseCase(passkeys=PasskeyCommandRepositoryORM(), webauthn=WebAuthnDuo(), retos=RetosEnCache())


def empezar_registro_passkey() -> IEmpezarRegistroPasskeyUseCase:
    return EmpezarRegistroPasskeyUseCase(
        passkeys=PasskeyCommandRepositoryORM(), webauthn=WebAuthnDuo(), retos=RetosEnCache()
    )


def registrar_passkey() -> IRegistrarPasskeyUseCase:
    return RegistrarPasskeyUseCase(
        passkeys=PasskeyCommandRepositoryORM(), webauthn=WebAuthnDuo(), retos=RetosEnCache(),
        eventos=PublicadorEventosDjango(), uow=UnidadDeTrabajoDjango(),
    )  # fmt: skip


def borrar_passkey() -> IBorrarPasskeyUseCase:
    return BorrarPasskeyUseCase(
        passkeys=PasskeyCommandRepositoryORM(), cuentas=CuentaCommandRepositoryORM(),
        identidades=IdentidadCommandRepositoryORM(), eventos=PublicadorEventosDjango(), uow=UnidadDeTrabajoDjango(),
    )  # fmt: skip


def entrar_con_passkey() -> IEntrarConPasskeyUseCase:
    return EntrarConPasskeyUseCase(
        passkeys=PasskeyCommandRepositoryORM(), webauthn=WebAuthnDuo(), retos=RetosEnCache(), inicio=iniciar_sesion()
    )
