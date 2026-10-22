"""Los fakes de las cuentas y los use cases montados con ellos (módulo 88). Contract tests:
tests/infrastructure/database/repositories/test_command_repositories.py."""

from core.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from usuarios.application.cambiar_contrasena_use_case.cambiar_contrasena_use_case import CambiarContrasenaUseCase
from usuarios.application.completar_registro_use_case.completar_registro_use_case import CompletarRegistroUseCase
from usuarios.application.confirmar_recuperacion_use_case.confirmar_recuperacion_use_case import (
    ConfirmarRecuperacionUseCase,
)
from usuarios.application.solicitar_recuperacion_use_case.solicitar_recuperacion_use_case import (
    SolicitarRecuperacionUseCase,
)
from usuarios.application.solicitar_registro_use_case.solicitar_registro_use_case import SolicitarRegistroUseCase
from usuarios.tests.fakes.cuenta_command_repository_fake import CuentaCommandRepositoryFake
from usuarios.tests.fakes.enlaces_fake import EnlacesFake
from usuarios.tests.fakes.politica_de_contrasenas_fake import PoliticaDeContrasenasFake
from usuarios.tests.fakes.sesiones_fake import SesionesFake


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
