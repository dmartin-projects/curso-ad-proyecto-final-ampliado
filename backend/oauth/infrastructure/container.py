# oauth/infrastructure/container.py — composition root del authorization server (módulo 90)
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from oauth.application.listar_aplicaciones_conectadas_use_case.i_listar_aplicaciones_conectadas_use_case import (
    IListarAplicacionesConectadasUseCase,
)
from oauth.application.listar_aplicaciones_conectadas_use_case.listar_aplicaciones_conectadas_use_case import (
    ListarAplicacionesConectadasUseCase,
)
from oauth.application.registrar_cliente_use_case.i_registrar_cliente_use_case import IRegistrarClienteUseCase
from oauth.application.registrar_cliente_use_case.registrar_cliente_use_case import RegistrarClienteUseCase
from oauth.application.retirar_acceso_use_case.i_retirar_acceso_use_case import IRetirarAccesoUseCase
from oauth.application.retirar_acceso_use_case.retirar_acceso_use_case import RetirarAccesoUseCase
from oauth.infrastructure.database.repositories.aplicacion_conectada_query_service_orm import (
    AplicacionConectadaQueryServiceORM,
)
from oauth.infrastructure.database.repositories.cliente_command_repository_orm import ClienteCommandRepositoryORM
from oauth.infrastructure.database.repositories.concesion_command_repository_orm import ConcesionCommandRepositoryORM


def registrar_cliente() -> IRegistrarClienteUseCase:
    return RegistrarClienteUseCase(clientes=ClienteCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


def retirar_acceso() -> IRetirarAccesoUseCase:  # ejercicio 1
    return RetirarAccesoUseCase(concesiones=ConcesionCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


def listar_aplicaciones_conectadas() -> IListarAplicacionesConectadasUseCase:  # ejercicio 1
    return ListarAplicacionesConectadasUseCase(aplicaciones=AplicacionConectadaQueryServiceORM())
