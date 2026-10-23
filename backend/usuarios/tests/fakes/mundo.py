"""Los fakes de las cuentas y los use cases montados con ellos (módulos 88 y 91). Contract tests:
tests/infrastructure/database/repositories/test_command_repositories.py."""

from core.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from usuarios.application.cambiar_contrasena_use_case.cambiar_contrasena_use_case import CambiarContrasenaUseCase
from usuarios.application.completar_login_social_use_case.completar_login_social_use_case import (
    CompletarLoginSocialUseCase,
)
from usuarios.application.completar_registro_use_case.completar_registro_use_case import CompletarRegistroUseCase
from usuarios.application.confirmar_recuperacion_use_case.confirmar_recuperacion_use_case import (
    ConfirmarRecuperacionUseCase,
)
from usuarios.application.desvincular_use_case.desvincular_use_case import DesvincularUseCase
from usuarios.application.empezar_login_social_use_case.empezar_login_social_use_case import EmpezarLoginSocialUseCase
from usuarios.application.establecer_contrasena_use_case.establecer_contrasena_use_case import (
    EstablecerContrasenaUseCase,
)
from usuarios.application.iniciar_sesion_use_case.iniciar_sesion_use_case import IniciarSesionUseCase
from usuarios.application.solicitar_recuperacion_use_case.solicitar_recuperacion_use_case import (
    SolicitarRecuperacionUseCase,
)
from usuarios.application.solicitar_registro_use_case.solicitar_registro_use_case import SolicitarRegistroUseCase
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.tests.fakes.cuenta_command_repository_fake import CuentaCommandRepositoryFake
from usuarios.tests.fakes.enlaces_fake import EnlacesFake
from usuarios.tests.fakes.identidad_command_repository_fake import IdentidadCommandRepositoryFake
from usuarios.tests.fakes.politica_de_contrasenas_fake import PoliticaDeContrasenasFake
from usuarios.tests.fakes.proveedor_identidad_fake import ProveedorIdentidadFake
from usuarios.tests.fakes.proveedores_fake import ProveedoresFake
from usuarios.tests.fakes.sesiones_fake import SesionesFake
from usuarios.tests.fakes.tokens_fake import TokensFake
from usuarios.tests.fakes.transacciones_fake import TransaccionesFake


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
        self.solicitar = SolicitarRecuperacionUseCase(**correo)
        self.confirmar = ConfirmarRecuperacionUseCase(**enlace)
        self.cambiar = CambiarContrasenaUseCase(
            cuentas=self.cuentas, politica=politica, sesiones=self.sesiones, uow=self.uow
        )
        # Módulo 91
        self.google = ProveedorIdentidadFake(Proveedor.GOOGLE)
        self.github = ProveedorIdentidadFake(Proveedor.GITHUB)
        self.proveedores = ProveedoresFake(self.google, self.github)
        self.transacciones, self.identidades = TransaccionesFake(), IdentidadCommandRepositoryFake()
        self.uow_social = UnidadDeTrabajoFake(self.cuentas, self.identidades)
        self.empezar = EmpezarLoginSocialUseCase(proveedores=self.proveedores, transacciones=self.transacciones)
        self.completar = CompletarLoginSocialUseCase(
            proveedores=self.proveedores, transacciones=self.transacciones, identidades=self.identidades,
            cuentas=self.cuentas, uow=self.uow_social,
        )  # fmt: skip
        self.desvincular = DesvincularUseCase(identidades=self.identidades, cuentas=self.cuentas, uow=self.uow_social)
        self.establecer = EstablecerContrasenaUseCase(cuentas=self.cuentas, politica=politica)
        self.iniciar_sesion = IniciarSesionUseCase(cuentas=self.cuentas, tokens=TokensFake())
