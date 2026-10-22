"""Todos los fakes y todos los use cases montados con ellos: lo que hace infrastructure/container.py, en memoria
(módulos 87 y 88).

Los fakes son la segunda implementación de cada interfaz. Se portan como los de verdad en lo que importa a los use
cases (ids, "de este hogar", duplicados, UPDATE condicional, transacción que se deshace). Que lo hagan igual lo
comprueban los contract tests de tests/infrastructure/database/repositories/, con los dos repositorios y los
mismos tests.
"""

from datetime import date

from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor
from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from core.tests.fakes.auditoria_fake import AuditoriaFake
from core.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from core.tests.fakes.reloj_fake import RelojFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from finanzas.application.apuntar_movimientos_use_case.apuntar_movimientos_use_case import ApuntarMovimientosUseCase
from finanzas.application.comprobar_presupuestos_use_case.comprobar_presupuestos_use_case import (
    ComprobarPresupuestosUseCase,
)
from finanzas.application.conciliar_movimientos_use_case.conciliar_movimientos_use_case import (
    ConciliarMovimientosUseCase,
)
from finanzas.application.crear_categoria_use_case.crear_categoria_use_case import CrearCategoriaUseCase
from finanzas.application.crear_categorias_por_defecto_use_case.crear_categorias_por_defecto_use_case import (
    CrearCategoriasPorDefectoUseCase,
)
from finanzas.application.crear_presupuesto_use_case.crear_presupuesto_use_case import CrearPresupuestoUseCase
from finanzas.application.descartar_propuestos_use_case.descartar_propuestos_use_case import DescartarPropuestosUseCase
from finanzas.application.desconciliar_movimientos_use_case.desconciliar_movimientos_use_case import (
    DesconciliarMovimientosUseCase,
)
from finanzas.application.eliminar_categoria_use_case.eliminar_categoria_use_case import EliminarCategoriaUseCase
from finanzas.application.eliminar_cuenta_use_case.eliminar_cuenta_use_case import EliminarCuentaUseCase
from finanzas.application.eliminar_movimiento_use_case.eliminar_movimiento_use_case import EliminarMovimientoUseCase
from finanzas.application.eliminar_movimientos_use_case.eliminar_movimientos_use_case import EliminarMovimientosUseCase
from finanzas.application.eliminar_presupuesto_use_case.eliminar_presupuesto_use_case import (
    EliminarPresupuestoUseCase,
)
from finanzas.application.modificar_categoria_use_case.modificar_categoria_use_case import ModificarCategoriaUseCase
from finanzas.application.modificar_movimiento_use_case.modificar_movimiento_use_case import (
    ModificarMovimientoUseCase,
)
from finanzas.application.modificar_presupuesto_use_case.modificar_presupuesto_use_case import (
    ModificarPresupuestoUseCase,
)
from finanzas.application.recategorizar_movimientos_use_case.recategorizar_movimientos_use_case import (
    RecategorizarMovimientosUseCase,
)
from finanzas.application.registrar_movimiento_use_case.registrar_movimiento_use_case import (
    RegistrarMovimientoUseCase,
)
from finanzas.application.reordenar_categorias_use_case.reordenar_categorias_use_case import (
    ReordenarCategoriasUseCase,
)
from finanzas.domain.bo.categoria import Categoria
from finanzas.domain.bo.movimiento import Movimiento
from finanzas.domain.bo.presupuesto import Presupuesto
from finanzas.tests.fakes.categoria_command_repository_fake import CategoriaCommandRepositoryFake
from finanzas.tests.fakes.cuenta_command_repository_fake import CuentaCommandRepositoryFake
from finanzas.tests.fakes.movimiento_command_repository_fake import MovimientoCommandRepositoryFake
from finanzas.tests.fakes.presupuesto_command_repository_fake import PresupuestoCommandRepositoryFake
from finanzas.tests.fakes.reconocedor_comercios_fake import ReconocedorComerciosFake

HOY = date(2026, 10, 15)
OCTUBRE = Mes(2026, 10)
HOGAR, OTRO_HOGAR = 1, 2


def actor(rol: Rol = Rol.MIEMBRO, usuario_id: int = 7) -> Actor:
    return Actor(usuario_id=usuario_id, rol=rol)


class Mundo:
    def __init__(self):
        self.movimientos = MovimientoCommandRepositoryFake()
        self.cuentas = CuentaCommandRepositoryFake(
            (HOGAR, 10), (HOGAR, 11), (OTRO_HOGAR, 20), movimientos=self.movimientos
        )
        self.categorias = CategoriaCommandRepositoryFake()
        self.presupuestos = PresupuestoCommandRepositoryFake(self.movimientos, self.categorias)
        self.comercios = ReconocedorComerciosFake(self.movimientos, self.categorias, mercadona=100)
        self.auditoria = AuditoriaFake()
        self.eventos = PublicadorEventosFake()
        self.uow = UnidadDeTrabajoFake(
            self.movimientos, self.cuentas, self.categorias, self.presupuestos, self.auditoria, self.eventos
        )
        comun = {"eventos": self.eventos, "uow": self.uow}
        repos = {"movimientos": self.movimientos, "categorias": self.categorias}
        reloj = {"reloj": RelojFake(HOY)}
        self.registrar = RegistrarMovimientoUseCase(
            **repos, cuentas=self.cuentas, comercios=self.comercios, auditoria=self.auditoria, **comun, **reloj
        )
        self.modificar = ModificarMovimientoUseCase(
            **repos, cuentas=self.cuentas, auditoria=self.auditoria, **comun, **reloj
        )
        self.eliminar = EliminarMovimientoUseCase(movimientos=self.movimientos, auditoria=self.auditoria, **comun)
        self.recategorizar = RecategorizarMovimientosUseCase(**repos, auditoria=self.auditoria, **comun)
        # módulo 88: en bloque y lo que apuntan los procesos
        borrar = {"movimientos": self.movimientos, "auditoria": self.auditoria, **comun}
        self.eliminar_varios = EliminarMovimientosUseCase(**borrar)
        self.descartar = DescartarPropuestosUseCase(**borrar)
        self.apuntar = ApuntarMovimientosUseCase(**repos, cuentas=self.cuentas, comercios=self.comercios, **comun)
        self.conciliar = ConciliarMovimientosUseCase(movimientos=self.movimientos, uow=self.uow)
        self.desconciliar = DesconciliarMovimientosUseCase(movimientos=self.movimientos, uow=self.uow)
        cats = {"categorias": self.categorias, **comun}
        self.crear_categoria = CrearCategoriaUseCase(**cats)
        self.modificar_categoria = ModificarCategoriaUseCase(**cats)
        self.eliminar_categoria = EliminarCategoriaUseCase(**cats)
        self.reordenar = ReordenarCategoriasUseCase(**cats)
        self.por_defecto = CrearCategoriasPorDefectoUseCase(categorias=self.categorias, uow=self.uow)
        pres = {"presupuestos": self.presupuestos, "categorias": self.categorias, **comun}
        self.crear_presupuesto = CrearPresupuestoUseCase(**pres)
        self.modificar_presupuesto = ModificarPresupuestoUseCase(**pres)
        self.eliminar_presupuesto = EliminarPresupuestoUseCase(presupuestos=self.presupuestos, **comun)
        self.comprobar = ComprobarPresupuestosUseCase(presupuestos=self.presupuestos, **comun)
        self.eliminar_cuenta = EliminarCuentaUseCase(cuentas=self.cuentas, uow=self.uow)  # ejercicio 1

    # ── Datos de partida (sin pasar por los use cases: así un test prueba UN use case) ──
    def categoria(self, nombre="Súper", hogar_id=HOGAR, padre: Categoria | None = None) -> Categoria:
        c = Categoria(hogar_id=hogar_id, nombre=nombre, padre_id=padre.id if padre else None)
        self.categorias.guardar(c)
        return c

    def movimiento(self, importe="-10", fecha=HOY, hogar_id=HOGAR, categoria: Categoria | None = None, **extra):
        m = Movimiento(
            hogar_id=hogar_id,
            cuenta_id=10 if hogar_id == HOGAR else 20,
            fecha=fecha,
            importe=Dinero(importe),
            concepto=extra.pop("concepto", "Compra"),
            categoria_id=categoria.id if categoria else None,
            **extra,
        )
        self.movimientos.guardar(m)
        return m

    def presupuesto(self, categoria: Categoria, importe="100", mes=OCTUBRE) -> Presupuesto:
        p = Presupuesto(HOGAR, categoria.id, mes, Dinero(importe))
        self.presupuestos.guardar(p)
        return p

    def limpiar_registros(self):
        self.eventos.publicados.clear()
        self.auditoria.registros.clear()
