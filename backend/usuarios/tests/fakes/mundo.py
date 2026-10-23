"""Los fakes de las cuentas y los use cases montados con ellos (módulos 88, 91 y 92, y sus ejercicios). Contract tests:
tests/infrastructure/database/repositories/test_command_repositories.py."""

from core.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from usuarios.application.borrar_passkey_use_case.borrar_passkey_use_case import BorrarPasskeyUseCase
from usuarios.application.cambiar_contrasena_use_case.cambiar_contrasena_use_case import CambiarContrasenaUseCase
from usuarios.application.completar_login_social_use_case.completar_login_social_use_case import (
    CompletarLoginSocialUseCase,
)
from usuarios.application.completar_registro_use_case.completar_registro_use_case import CompletarRegistroUseCase
from usuarios.application.completar_segundo_factor_use_case.completar_segundo_factor_use_case import (
    CompletarSegundoFactorUseCase,
)
from usuarios.application.confirmar_recuperacion_use_case.confirmar_recuperacion_use_case import (
    ConfirmarRecuperacionUseCase,
)
from usuarios.application.confirmar_totp_use_case.confirmar_totp_use_case import ConfirmarTotpUseCase
from usuarios.application.desactivar_mfa_use_case.desactivar_mfa_use_case import DesactivarMfaUseCase
from usuarios.application.desvincular_use_case.desvincular_use_case import DesvincularUseCase
from usuarios.application.empezar_login_social_use_case.empezar_login_social_use_case import EmpezarLoginSocialUseCase
from usuarios.application.empezar_registro_passkey_use_case.empezar_registro_passkey_use_case import (
    EmpezarRegistroPasskeyUseCase,
)
from usuarios.application.empezar_totp_use_case.empezar_totp_use_case import EmpezarTotpUseCase
from usuarios.application.entrar_con_passkey_use_case.entrar_con_passkey_use_case import EntrarConPasskeyUseCase
from usuarios.application.establecer_contrasena_use_case.establecer_contrasena_use_case import (
    EstablecerContrasenaUseCase,
)
from usuarios.application.iniciar_sesion_use_case.iniciar_sesion_use_case import IniciarSesionUseCase
from usuarios.application.pedir_reto_use_case.pedir_reto_use_case import PedirRetoUseCase
from usuarios.application.reautenticar_use_case.reautenticar_use_case import ReautenticarUseCase
from usuarios.application.regenerar_codigos_use_case.regenerar_codigos_use_case import RegenerarCodigosUseCase
from usuarios.application.registrar_passkey_use_case.registrar_passkey_use_case import RegistrarPasskeyUseCase
from usuarios.application.renovar_sesion_use_case.renovar_sesion_use_case import RenovarSesionUseCase
from usuarios.application.shared.apertura_de_sesion import AperturaDeSesion
from usuarios.application.shared.comprobar_factor import ComprobarFactor
from usuarios.application.shared.factores_de_cuenta import FactoresDeCuenta
from usuarios.application.solicitar_recuperacion_use_case.solicitar_recuperacion_use_case import (
    SolicitarRecuperacionUseCase,
)
from usuarios.application.solicitar_registro_use_case.solicitar_registro_use_case import SolicitarRegistroUseCase
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.tests.fakes.codigo_qr_fake import CodigoQrFake
from usuarios.tests.fakes.codigos_de_recuperacion_fake import CodigosDeRecuperacionFake
from usuarios.tests.fakes.cuenta_command_repository_fake import CuentaCommandRepositoryFake
from usuarios.tests.fakes.enlaces_fake import EnlacesFake
from usuarios.tests.fakes.identidad_command_repository_fake import IdentidadCommandRepositoryFake
from usuarios.tests.fakes.passkey_command_repository_fake import PasskeyCommandRepositoryFake
from usuarios.tests.fakes.pendientes_fake import PendientesFake
from usuarios.tests.fakes.politica_de_contrasenas_fake import PoliticaDeContrasenasFake
from usuarios.tests.fakes.proveedor_identidad_fake import ProveedorIdentidadFake
from usuarios.tests.fakes.proveedores_fake import ProveedoresFake
from usuarios.tests.fakes.reloj_del_sistema_fake import RelojDelSistemaFake
from usuarios.tests.fakes.retos_fake import RetosFake
from usuarios.tests.fakes.segundo_factor_command_repository_fake import SegundoFactorCommandRepositoryFake
from usuarios.tests.fakes.sesiones_fake import SesionesFake
from usuarios.tests.fakes.tokens_fake import TokensFake
from usuarios.tests.fakes.totp_fake import TotpFake
from usuarios.tests.fakes.transacciones_fake import TransaccionesFake
from usuarios.tests.fakes.webauthn_fake import WebAuthnFake


class Mundo:
    def __init__(self):
        self.cuentas, self.sesiones, self.eventos = (
            CuentaCommandRepositoryFake(),
            SesionesFake(),
            PublicadorEventosFake(),
        )
        self.uow = UnidadDeTrabajoFake(self.cuentas, self.sesiones, self.eventos)
        politica, enlaces = PoliticaDeContrasenasFake(), EnlacesFake()
        correo = {"cuentas": self.cuentas, "enlaces": enlaces, "eventos": self.eventos, "uow": self.uow}
        enlace = {"cuentas": self.cuentas, "politica": politica, "enlaces": enlaces}
        self.registrar = SolicitarRegistroUseCase(**correo)
        self.completar_registro = CompletarRegistroUseCase(**enlace)
        self.segundos = (
            SegundoFactorCommandRepositoryFake()
        )  # (módulo 92: también los usan la recuperación y el ejercicio 3)
        self.reloj = RelojDelSistemaFake()
        self.solicitar = SolicitarRecuperacionUseCase(**correo)
        self.confirmar = ConfirmarRecuperacionUseCase(
            **enlace, sesiones=self.sesiones, segundos=self.segundos, eventos=self.eventos, uow=self.uow
        )
        self.cambiar = CambiarContrasenaUseCase(
            cuentas=self.cuentas, politica=politica, sesiones=self.sesiones, uow=self.uow
        )
        # Módulo 91
        self.google = ProveedorIdentidadFake(Proveedor.GOOGLE)
        self.github = ProveedorIdentidadFake(Proveedor.GITHUB)
        self.proveedores = ProveedoresFake(self.google, self.github)
        self.transacciones, self.identidades = TransaccionesFake(), IdentidadCommandRepositoryFake()
        self.uow_social = UnidadDeTrabajoFake(self.cuentas, self.identidades, self.eventos)
        self.empezar = EmpezarLoginSocialUseCase(
            proveedores=self.proveedores, transacciones=self.transacciones, reloj=self.reloj
        )
        self.completar = CompletarLoginSocialUseCase(
            proveedores=self.proveedores, transacciones=self.transacciones, identidades=self.identidades,
            cuentas=self.cuentas, eventos=self.eventos, uow=self.uow_social, sesiones=self.sesiones,
            segundos=self.segundos, reloj=self.reloj,
        )  # fmt: skip
        # Módulo 92
        self.totp, self.codigos = TotpFake(), CodigosDeRecuperacionFake()
        self.passkeys, self.webauthn, self.retos, self.pendientes = (
            PasskeyCommandRepositoryFake(), WebAuthnFake(), RetosFake(), PendientesFake()
        )  # fmt: skip
        self.uow_mfa = UnidadDeTrabajoFake(self.segundos, self.passkeys, self.sesiones, self.eventos)
        self.desvincular = DesvincularUseCase(
            identidades=self.identidades, cuentas=self.cuentas, passkeys=self.passkeys, uow=self.uow_social
        )
        self.establecer = EstablecerContrasenaUseCase(cuentas=self.cuentas, politica=politica)
        factores = FactoresDeCuenta(
            cuentas=self.cuentas, segundos=self.segundos, codigos=self.codigos, passkeys=self.passkeys
        )
        apertura = AperturaDeSesion(sesiones=self.sesiones, tokens=TokensFake(), eventos=self.eventos, uow=self.uow_mfa)
        self.iniciar_sesion = IniciarSesionUseCase(
            cuentas=self.cuentas, segundos=self.segundos, pendientes=self.pendientes, factores=factores,
            apertura=apertura, reloj=self.reloj,
        )  # fmt: skip
        self.comprobar = ComprobarFactor(
            cuentas=self.cuentas, segundos=self.segundos, totp=self.totp, codigos=self.codigos,
            passkeys=self.passkeys, webauthn=self.webauthn, retos=self.retos, eventos=self.eventos, reloj=self.reloj,
        )  # fmt: skip
        self.segundo_paso = CompletarSegundoFactorUseCase(
            apertura=apertura, comprobar=self.comprobar, pendientes=self.pendientes, uow=self.uow_mfa, reloj=self.reloj
        )
        self.reautenticar = ReautenticarUseCase(
            factores=factores, comprobar=self.comprobar, sesiones=self.sesiones, uow=self.uow_mfa, reloj=self.reloj
        )
        self.renovar = RenovarSesionUseCase(sesiones=self.sesiones, eventos=self.eventos, uow=self.uow_mfa)
        self.empezar_totp = EmpezarTotpUseCase(
            segundos=self.segundos, totp=self.totp, qr=CodigoQrFake(), uow=self.uow_mfa
        )
        self.confirmar_totp = ConfirmarTotpUseCase(
            segundos=self.segundos, totp=self.totp, codigos=self.codigos, eventos=self.eventos, uow=self.uow_mfa,
            reloj=self.reloj,
        )  # fmt: skip
        self.desactivar_mfa = DesactivarMfaUseCase(
            segundos=self.segundos, codigos=self.codigos, eventos=self.eventos, uow=self.uow_mfa
        )
        self.regenerar_codigos = RegenerarCodigosUseCase(  # ejercicio 2
            segundos=self.segundos, codigos=self.codigos, eventos=self.eventos, uow=self.uow_mfa
        )
        web = {"passkeys": self.passkeys, "webauthn": self.webauthn, "retos": self.retos}
        self.pedir_reto = PedirRetoUseCase(**web)
        self.empezar_registro = EmpezarRegistroPasskeyUseCase(**web)
        self.registrar_passkey = RegistrarPasskeyUseCase(eventos=self.eventos, uow=self.uow_mfa, **web)
        self.borrar_passkey = BorrarPasskeyUseCase(
            passkeys=self.passkeys, cuentas=self.cuentas, identidades=self.identidades, eventos=self.eventos,
            uow=self.uow_mfa,
        )  # fmt: skip
        self.entrar_con_passkey = EntrarConPasskeyUseCase(inicio=self.iniciar_sesion, **web)
