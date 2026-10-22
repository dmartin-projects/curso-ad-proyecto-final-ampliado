"""Los fakes del authorization server y los use cases montados con ellos (módulo 90). Contract tests:
tests/infrastructure/database/repositories/test_command_repositories.py."""

from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from oauth.application.registrar_cliente_use_case.registrar_cliente_use_case import RegistrarClienteUseCase
from oauth.application.retirar_acceso_use_case.retirar_acceso_use_case import RetirarAccesoUseCase
from oauth.tests.fakes.cliente_command_repository_fake import ClienteCommandRepositoryFake
from oauth.tests.fakes.concesion_command_repository_fake import ConcesionCommandRepositoryFake


class Mundo:
    def __init__(self):
        self.clientes, self.concesiones = ClienteCommandRepositoryFake(), ConcesionCommandRepositoryFake()
        self.uow = UnidadDeTrabajoFake(self.clientes, self.concesiones)
        self.registrar = RegistrarClienteUseCase(clientes=self.clientes, uow=self.uow)
        self.retirar = RetirarAccesoUseCase(concesiones=self.concesiones, uow=self.uow)
