# usuarios/infrastructure/container.py — composition root de las cuentas (módulos 88 y 91)
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from usuarios.application.cambiar_contrasena_use_case.cambiar_contrasena_use_case import CambiarContrasenaUseCase
from usuarios.application.cambiar_contrasena_use_case.i_cambiar_contrasena_use_case import ICambiarContrasenaUseCase
from usuarios.application.completar_login_social_use_case.completar_login_social_use_case import (
    CompletarLoginSocialUseCase,
)
from usuarios.application.completar_login_social_use_case.i_completar_login_social_use_case import (
    ICompletarLoginSocialUseCase,
)
from usuarios.application.completar_registro_use_case.completar_registro_use_case import CompletarRegistroUseCase
from usuarios.application.completar_registro_use_case.i_completar_registro_use_case import ICompletarRegistroUseCase
from usuarios.application.confirmar_recuperacion_use_case.confirmar_recuperacion_use_case import (
    ConfirmarRecuperacionUseCase,
)
from usuarios.application.confirmar_recuperacion_use_case.i_confirmar_recuperacion_use_case import (
    IConfirmarRecuperacionUseCase,
)
from usuarios.application.desvincular_use_case.desvincular_use_case import DesvincularUseCase
from usuarios.application.desvincular_use_case.i_desvincular_use_case import IDesvincularUseCase
from usuarios.application.empezar_login_social_use_case.empezar_login_social_use_case import EmpezarLoginSocialUseCase
from usuarios.application.empezar_login_social_use_case.i_empezar_login_social_use_case import (
    IEmpezarLoginSocialUseCase,
)
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
from usuarios.application.obtener_acceso_use_case.i_obtener_acceso_use_case import IObtenerAccesoUseCase
from usuarios.application.obtener_acceso_use_case.obtener_acceso_use_case import ObtenerAccesoUseCase
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
from usuarios.infrastructure.auth.tokens_simple_jwt import TokensSimpleJWT
from usuarios.infrastructure.cache.transacciones_en_cache import TransaccionesEnCache
from usuarios.infrastructure.database.repositories.acceso_query_service_orm import AccesoQueryServiceORM
from usuarios.infrastructure.database.repositories.cuenta_command_repository_orm import CuentaCommandRepositoryORM
from usuarios.infrastructure.database.repositories.identidad_command_repository_orm import (
    IdentidadCommandRepositoryORM,
)
from usuarios.infrastructure.messaging.publicador_eventos_django import PublicadorEventosDjango
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
        cuentas=CuentaCommandRepositoryORM(), politica=PoliticaDeContrasenasDjango(), enlaces=EnlacesDjango()
    )


def cambiar_contrasena() -> ICambiarContrasenaUseCase:
    return CambiarContrasenaUseCase(
        cuentas=CuentaCommandRepositoryORM(),
        politica=PoliticaDeContrasenasDjango(),
        sesiones=SesionesSimpleJWT(),
        uow=UnidadDeTrabajoDjango(),
    )


# ── Módulo 91: sesiones y social login ──


def iniciar_sesion() -> IIniciarSesionUseCase:
    return IniciarSesionUseCase(cuentas=CuentaCommandRepositoryORM(), tokens=TokensSimpleJWT())


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
        identidades=IdentidadCommandRepositoryORM(), cuentas=CuentaCommandRepositoryORM(), uow=UnidadDeTrabajoDjango()
    )


def establecer_contrasena() -> IEstablecerContrasenaUseCase:
    return EstablecerContrasenaUseCase(cuentas=CuentaCommandRepositoryORM(), politica=PoliticaDeContrasenasDjango())


def obtener_acceso() -> IObtenerAccesoUseCase:
    return ObtenerAccesoUseCase(acceso=AccesoQueryServiceORM())
