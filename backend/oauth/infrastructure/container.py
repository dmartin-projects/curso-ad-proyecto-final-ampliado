# oauth/infrastructure/container.py — composition root del authorization server (módulo 90)
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from oauth.application.registrar_cliente_use_case.i_registrar_cliente_use_case import IRegistrarClienteUseCase
from oauth.application.registrar_cliente_use_case.registrar_cliente_use_case import RegistrarClienteUseCase
from oauth.infrastructure.database.repositories.cliente_command_repository_orm import ClienteCommandRepositoryORM


def registrar_cliente() -> IRegistrarClienteUseCase:
    return RegistrarClienteUseCase(clientes=ClienteCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())
