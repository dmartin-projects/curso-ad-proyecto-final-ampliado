# usuarios/infrastructure/container.py — composition root de las cuentas (módulo 88)
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from usuarios.application.cambiar_contrasena_use_case.cambiar_contrasena_use_case import CambiarContrasenaUseCase
from usuarios.application.cambiar_contrasena_use_case.i_cambiar_contrasena_use_case import ICambiarContrasenaUseCase
from usuarios.application.completar_registro_use_case.completar_registro_use_case import CompletarRegistroUseCase
from usuarios.application.completar_registro_use_case.i_completar_registro_use_case import ICompletarRegistroUseCase
from usuarios.application.confirmar_recuperacion_use_case.confirmar_recuperacion_use_case import (
    ConfirmarRecuperacionUseCase,
)
from usuarios.application.confirmar_recuperacion_use_case.i_confirmar_recuperacion_use_case import (
    IConfirmarRecuperacionUseCase,
)
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
from usuarios.infrastructure.auth.sesiones_simple_jwt import SesionesSimpleJWT
from usuarios.infrastructure.database.repositories.cuenta_command_repository_orm import CuentaCommandRepositoryORM
from usuarios.infrastructure.messaging.publicador_eventos_django import PublicadorEventosDjango


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
        cuentas=CuentaCommandRepositoryORM(), politica=PoliticaDeContrasenasDjango(), enlaces=EnlacesDjango()
    )


def cambiar_contrasena() -> ICambiarContrasenaUseCase:
    return CambiarContrasenaUseCase(
        cuentas=CuentaCommandRepositoryORM(),
        politica=PoliticaDeContrasenasDjango(),
        sesiones=SesionesSimpleJWT(),
        uow=UnidadDeTrabajoDjango(),
    )
