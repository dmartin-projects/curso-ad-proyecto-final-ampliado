# finanzas/infrastructure/container.py — composition root de finanzas (módulos 87 y 88)
#
# El ÚNICO sitio que sabe qué implementación va detrás de cada interfaz. Las views, las tareas, los receivers y los
# comandos piden aquí su use case ya montado; nadie más escribe `RegistrarMovimientoUseCase(MovimientoCommand…)`.
# Una función por use case: es el papel de una factory, pero aquí, en infraestructura, y no en application
# (una factory en application tendría que importar los adapters y rompería la regla de dependencias).
# Funciones y no un framework de DI: montar un use case cuesta microsegundos (los adapters no guardan estado) y se
# lee de un vistazo. En un test con base de datos, una pieza se cambia con monkeypatch (ejercicio 3).
from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.auditoria_django import AuditoriaDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from eventos.infrastructure import container as eventos
from finanzas.application.apuntar_movimientos_use_case.apuntar_movimientos_use_case import ApuntarMovimientosUseCase
from finanzas.application.apuntar_movimientos_use_case.i_apuntar_movimientos_use_case import IApuntarMovimientosUseCase
from finanzas.application.comprobar_presupuestos_use_case.comprobar_presupuestos_use_case import (
    ComprobarPresupuestosUseCase,
)
from finanzas.application.comprobar_presupuestos_use_case.i_comprobar_presupuestos_use_case import (
    IComprobarPresupuestosUseCase,
)
from finanzas.application.conciliar_movimientos_use_case.conciliar_movimientos_use_case import (
    ConciliarMovimientosUseCase,
)
from finanzas.application.conciliar_movimientos_use_case.i_conciliar_movimientos_use_case import (
    IConciliarMovimientosUseCase,
)
from finanzas.application.crear_categoria_use_case.crear_categoria_use_case import CrearCategoriaUseCase
from finanzas.application.crear_categoria_use_case.i_crear_categoria_use_case import ICrearCategoriaUseCase
from finanzas.application.crear_categorias_por_defecto_use_case.crear_categorias_por_defecto_use_case import (
    CrearCategoriasPorDefectoUseCase,
)
from finanzas.application.crear_categorias_por_defecto_use_case.i_crear_categorias_por_defecto_use_case import (
    ICrearCategoriasPorDefectoUseCase,
)
from finanzas.application.crear_presupuesto_use_case.crear_presupuesto_use_case import CrearPresupuestoUseCase
from finanzas.application.crear_presupuesto_use_case.i_crear_presupuesto_use_case import ICrearPresupuestoUseCase
from finanzas.application.descartar_propuestos_use_case.descartar_propuestos_use_case import DescartarPropuestosUseCase
from finanzas.application.descartar_propuestos_use_case.i_descartar_propuestos_use_case import (
    IDescartarPropuestosUseCase,
)
from finanzas.application.desconciliar_movimientos_use_case.desconciliar_movimientos_use_case import (
    DesconciliarMovimientosUseCase,
)
from finanzas.application.desconciliar_movimientos_use_case.i_desconciliar_movimientos_use_case import (
    IDesconciliarMovimientosUseCase,
)
from finanzas.application.eliminar_categoria_use_case.eliminar_categoria_use_case import EliminarCategoriaUseCase
from finanzas.application.eliminar_categoria_use_case.i_eliminar_categoria_use_case import IEliminarCategoriaUseCase
from finanzas.application.eliminar_cuenta_use_case.eliminar_cuenta_use_case import EliminarCuentaUseCase
from finanzas.application.eliminar_cuenta_use_case.i_eliminar_cuenta_use_case import IEliminarCuentaUseCase
from finanzas.application.eliminar_movimiento_use_case.eliminar_movimiento_use_case import EliminarMovimientoUseCase
from finanzas.application.eliminar_movimiento_use_case.i_eliminar_movimiento_use_case import (
    IEliminarMovimientoUseCase,
)
from finanzas.application.eliminar_movimientos_use_case.eliminar_movimientos_use_case import EliminarMovimientosUseCase
from finanzas.application.eliminar_movimientos_use_case.i_eliminar_movimientos_use_case import (
    IEliminarMovimientosUseCase,
)
from finanzas.application.eliminar_presupuesto_use_case.eliminar_presupuesto_use_case import (
    EliminarPresupuestoUseCase,
)
from finanzas.application.eliminar_presupuesto_use_case.i_eliminar_presupuesto_use_case import (
    IEliminarPresupuestoUseCase,
)
from finanzas.application.exportar_movimientos_use_case.exportar_movimientos_use_case import ExportarMovimientosUseCase
from finanzas.application.exportar_movimientos_use_case.i_exportar_movimientos_use_case import (
    IExportarMovimientosUseCase,
)
from finanzas.application.listar_categorias_use_case.i_listar_categorias_use_case import IListarCategoriasUseCase
from finanzas.application.listar_categorias_use_case.listar_categorias_use_case import ListarCategoriasUseCase
from finanzas.application.listar_comercios_use_case.i_listar_comercios_use_case import IListarComerciosUseCase
from finanzas.application.listar_comercios_use_case.listar_comercios_use_case import ListarComerciosUseCase
from finanzas.application.listar_cuentas_use_case.i_listar_cuentas_use_case import IListarCuentasUseCase
from finanzas.application.listar_cuentas_use_case.listar_cuentas_use_case import ListarCuentasUseCase
from finanzas.application.listar_movimientos_use_case.i_listar_movimientos_use_case import IListarMovimientosUseCase
from finanzas.application.listar_movimientos_use_case.listar_movimientos_use_case import ListarMovimientosUseCase
from finanzas.application.listar_presupuestos_use_case.i_listar_presupuestos_use_case import IListarPresupuestosUseCase
from finanzas.application.listar_presupuestos_use_case.listar_presupuestos_use_case import ListarPresupuestosUseCase
from finanzas.application.modificar_categoria_use_case.i_modificar_categoria_use_case import (
    IModificarCategoriaUseCase,
)
from finanzas.application.modificar_categoria_use_case.modificar_categoria_use_case import ModificarCategoriaUseCase
from finanzas.application.modificar_movimiento_use_case.i_modificar_movimiento_use_case import (
    IModificarMovimientoUseCase,
)
from finanzas.application.modificar_movimiento_use_case.modificar_movimiento_use_case import (
    ModificarMovimientoUseCase,
)
from finanzas.application.modificar_presupuesto_use_case.i_modificar_presupuesto_use_case import (
    IModificarPresupuestoUseCase,
)
from finanzas.application.modificar_presupuesto_use_case.modificar_presupuesto_use_case import (
    ModificarPresupuestoUseCase,
)
from finanzas.application.obtener_categoria_use_case.i_obtener_categoria_use_case import IObtenerCategoriaUseCase
from finanzas.application.obtener_categoria_use_case.obtener_categoria_use_case import ObtenerCategoriaUseCase
from finanzas.application.obtener_cuenta_use_case.i_obtener_cuenta_use_case import IObtenerCuentaUseCase
from finanzas.application.obtener_cuenta_use_case.obtener_cuenta_use_case import ObtenerCuentaUseCase
from finanzas.application.obtener_dashboard_use_case.i_obtener_dashboard_use_case import IObtenerDashboardUseCase
from finanzas.application.obtener_dashboard_use_case.obtener_dashboard_use_case import ObtenerDashboardUseCase
from finanzas.application.obtener_movimiento_use_case.i_obtener_movimiento_use_case import IObtenerMovimientoUseCase
from finanzas.application.obtener_movimiento_use_case.obtener_movimiento_use_case import ObtenerMovimientoUseCase
from finanzas.application.obtener_presupuesto_use_case.i_obtener_presupuesto_use_case import IObtenerPresupuestoUseCase
from finanzas.application.obtener_presupuesto_use_case.obtener_presupuesto_use_case import ObtenerPresupuestoUseCase
from finanzas.application.recategorizar_movimientos_use_case.i_recategorizar_movimientos_use_case import (
    IRecategorizarMovimientosUseCase,
)
from finanzas.application.recategorizar_movimientos_use_case.recategorizar_movimientos_use_case import (
    RecategorizarMovimientosUseCase,
)
from finanzas.application.registrar_movimiento_use_case.i_registrar_movimiento_use_case import (
    IRegistrarMovimientoUseCase,
)
from finanzas.application.registrar_movimiento_use_case.registrar_movimiento_use_case import (
    RegistrarMovimientoUseCase,
)
from finanzas.application.reordenar_categorias_use_case.i_reordenar_categorias_use_case import (
    IReordenarCategoriasUseCase,
)
from finanzas.application.reordenar_categorias_use_case.reordenar_categorias_use_case import (
    ReordenarCategoriasUseCase,
)
from finanzas.infrastructure.cache.dashboard_cache import DashboardQueryServiceCache
from finanzas.infrastructure.database.repositories.categoria_command_repository_orm import (
    CategoriaCommandRepositoryORM,
)
from finanzas.infrastructure.database.repositories.categoria_query_service_orm import CategoriaQueryServiceORM
from finanzas.infrastructure.database.repositories.comercio_query_service_orm import ComercioQueryServiceORM
from finanzas.infrastructure.database.repositories.cuenta_command_repository_orm import CuentaCommandRepositoryORM
from finanzas.infrastructure.database.repositories.cuenta_query_service_orm import CuentaQueryServiceORM
from finanzas.infrastructure.database.repositories.dashboard_query_service_orm import DashboardQueryServiceORM
from finanzas.infrastructure.database.repositories.movimiento_command_repository_orm import (
    MovimientoCommandRepositoryORM,
)
from finanzas.infrastructure.database.repositories.movimiento_query_service_orm import MovimientoQueryServiceORM
from finanzas.infrastructure.database.repositories.presupuesto_command_repository_orm import (
    PresupuestoCommandRepositoryORM,
)
from finanzas.infrastructure.database.repositories.presupuesto_query_service_orm import PresupuestoQueryServiceORM
from finanzas.infrastructure.database.services.reconocedor_comercios_orm import ReconocedorComerciosORM
from finanzas.infrastructure.messaging.publicador_eventos_django import PublicadorEventosDjango


def _transaccion_y_eventos() -> dict:
    return {"uow": UnidadDeTrabajoDjango(), "eventos": PublicadorEventosDjango(outbox=eventos.outbox())}


# ── Movimientos ──
def registrar_movimiento() -> IRegistrarMovimientoUseCase:
    return RegistrarMovimientoUseCase(
        movimientos=MovimientoCommandRepositoryORM(),
        cuentas=CuentaCommandRepositoryORM(),
        categorias=CategoriaCommandRepositoryORM(),
        comercios=ReconocedorComerciosORM(),
        auditoria=AuditoriaDjango(),
        reloj=RelojDjango(),
        **_transaccion_y_eventos(),
    )


def modificar_movimiento() -> IModificarMovimientoUseCase:
    return ModificarMovimientoUseCase(
        movimientos=MovimientoCommandRepositoryORM(),
        cuentas=CuentaCommandRepositoryORM(),
        categorias=CategoriaCommandRepositoryORM(),
        auditoria=AuditoriaDjango(),
        reloj=RelojDjango(),
        **_transaccion_y_eventos(),
    )


def eliminar_movimiento() -> IEliminarMovimientoUseCase:
    return EliminarMovimientoUseCase(
        movimientos=MovimientoCommandRepositoryORM(), auditoria=AuditoriaDjango(), **_transaccion_y_eventos()
    )


def recategorizar_movimientos() -> IRecategorizarMovimientosUseCase:
    return RecategorizarMovimientosUseCase(
        movimientos=MovimientoCommandRepositoryORM(),
        categorias=CategoriaCommandRepositoryORM(),
        auditoria=AuditoriaDjango(),
        **_transaccion_y_eventos(),
    )


def eliminar_movimientos() -> IEliminarMovimientosUseCase:
    return EliminarMovimientosUseCase(
        movimientos=MovimientoCommandRepositoryORM(), auditoria=AuditoriaDjango(), **_transaccion_y_eventos()
    )


def descartar_propuestos() -> IDescartarPropuestosUseCase:
    return DescartarPropuestosUseCase(
        movimientos=MovimientoCommandRepositoryORM(), auditoria=AuditoriaDjango(), **_transaccion_y_eventos()
    )


# ── Lo que apuntan los procesos: tickets, extractos, el seed (módulo 88) ──
def apuntar_movimientos() -> IApuntarMovimientosUseCase:
    return ApuntarMovimientosUseCase(
        movimientos=MovimientoCommandRepositoryORM(),
        cuentas=CuentaCommandRepositoryORM(),
        categorias=CategoriaCommandRepositoryORM(),
        comercios=ReconocedorComerciosORM(),
        **_transaccion_y_eventos(),
    )


def conciliar_movimientos() -> IConciliarMovimientosUseCase:
    return ConciliarMovimientosUseCase(movimientos=MovimientoCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


def desconciliar_movimientos() -> IDesconciliarMovimientosUseCase:
    return DesconciliarMovimientosUseCase(movimientos=MovimientoCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


# ── Categorías ──
def crear_categoria() -> ICrearCategoriaUseCase:
    return CrearCategoriaUseCase(categorias=CategoriaCommandRepositoryORM(), **_transaccion_y_eventos())


def modificar_categoria() -> IModificarCategoriaUseCase:
    return ModificarCategoriaUseCase(categorias=CategoriaCommandRepositoryORM(), **_transaccion_y_eventos())


def eliminar_categoria() -> IEliminarCategoriaUseCase:
    return EliminarCategoriaUseCase(categorias=CategoriaCommandRepositoryORM(), **_transaccion_y_eventos())


def reordenar_categorias() -> IReordenarCategoriasUseCase:
    return ReordenarCategoriasUseCase(categorias=CategoriaCommandRepositoryORM(), **_transaccion_y_eventos())


def crear_categorias_por_defecto() -> ICrearCategoriasPorDefectoUseCase:
    return CrearCategoriasPorDefectoUseCase(categorias=CategoriaCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


# ── Presupuestos ──
def crear_presupuesto() -> ICrearPresupuestoUseCase:
    return CrearPresupuestoUseCase(
        presupuestos=PresupuestoCommandRepositoryORM(),
        categorias=CategoriaCommandRepositoryORM(),
        **_transaccion_y_eventos(),
    )


def modificar_presupuesto() -> IModificarPresupuestoUseCase:
    return ModificarPresupuestoUseCase(
        presupuestos=PresupuestoCommandRepositoryORM(),
        categorias=CategoriaCommandRepositoryORM(),
        **_transaccion_y_eventos(),
    )


def eliminar_presupuesto() -> IEliminarPresupuestoUseCase:
    return EliminarPresupuestoUseCase(presupuestos=PresupuestoCommandRepositoryORM(), **_transaccion_y_eventos())


def comprobar_presupuestos() -> IComprobarPresupuestosUseCase:
    return ComprobarPresupuestosUseCase(presupuestos=PresupuestoCommandRepositoryORM(), **_transaccion_y_eventos())


# ── Lectura: un use case de consulta por listado y por detalle, cada uno con su query service ──
def listar_movimientos() -> IListarMovimientosUseCase:
    return ListarMovimientosUseCase(movimientos=MovimientoQueryServiceORM())


def obtener_movimiento() -> IObtenerMovimientoUseCase:
    return ObtenerMovimientoUseCase(movimientos=MovimientoQueryServiceORM())


def exportar_movimientos() -> IExportarMovimientosUseCase:
    return ExportarMovimientosUseCase(movimientos=MovimientoQueryServiceORM())


def listar_categorias() -> IListarCategoriasUseCase:
    return ListarCategoriasUseCase(categorias=CategoriaQueryServiceORM())


def obtener_categoria() -> IObtenerCategoriaUseCase:
    return ObtenerCategoriaUseCase(categorias=CategoriaQueryServiceORM())


def listar_cuentas() -> IListarCuentasUseCase:
    return ListarCuentasUseCase(cuentas=CuentaQueryServiceORM())


def obtener_cuenta() -> IObtenerCuentaUseCase:
    return ObtenerCuentaUseCase(cuentas=CuentaQueryServiceORM())


def listar_presupuestos() -> IListarPresupuestosUseCase:
    return ListarPresupuestosUseCase(presupuestos=PresupuestoQueryServiceORM())


def obtener_presupuesto() -> IObtenerPresupuestoUseCase:
    return ObtenerPresupuestoUseCase(presupuestos=PresupuestoQueryServiceORM())


def listar_comercios() -> IListarComerciosUseCase:
    return ListarComerciosUseCase(comercios=ComercioQueryServiceORM())


# ── Dashboard (lectura) ──
def obtener_dashboard() -> IObtenerDashboardUseCase:
    # el query service del ORM, envuelto en la caché: el use case no sabe que la hay
    return ObtenerDashboardUseCase(dashboard=DashboardQueryServiceCache(DashboardQueryServiceORM()))


# ── Cuentas (ejercicio 1) ──
def eliminar_cuenta() -> IEliminarCuentaUseCase:
    return EliminarCuentaUseCase(cuentas=CuentaCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())
