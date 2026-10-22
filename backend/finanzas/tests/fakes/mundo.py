"""Todos los fakes y todos los use cases montados con ellos: lo que hace infrastructure/container.py, en memoria
(módulo 87).

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
from finanzas.application.comprobar_presupuestos_use_case.comprobar_presupuestos_use_case import (
    ComprobarPresupuestosUseCase,
)
from finanzas.application.crear_categoria_use_case.crear_categoria_use_case import CrearCategoriaUseCase
from finanzas.application.crear_categorias_por_defecto_use_case.crear_categorias_por_defecto_use_case import (
    CrearCategoriasPorDefectoUseCase,
)
from finanzas.application.crear_presupuesto_use_case.crear_presupuesto_use_case import CrearPresupuestoUseCase
from finanzas.application.eliminar_categoria_use_case.eliminar_categoria_use_case import EliminarCategoriaUseCase
from finanzas.application.eliminar_movimiento_use_case.eliminar_movimiento_use_case import EliminarMovimientoUseCase
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
from finanzas.tests.fakes.auditoria_fake import AuditoriaFake
from finanzas.tests.fakes.categoria_command_repository_fake import CategoriaCommandRepositoryFake
from finanzas.tests.fakes.cuenta_command_repository_fake import CuentaCommandRepositoryFake
from finanzas.tests.fakes.movimiento_command_repository_fake import MovimientoCommandRepositoryFake
from finanzas.tests.fakes.presupuesto_command_repository_fake import PresupuestoCommandRepositoryFake
from finanzas.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from finanzas.tests.fakes.reconocedor_comercios_fake import ReconocedorComerciosFake
from finanzas.tests.fakes.reloj_fake import RelojFake
from finanzas.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake

HOY = date(2026, 10, 15)
OCTUBRE = Mes(2026, 10)
HOGAR, OTRO_HOGAR = 1, 2


def actor(rol: Rol = Rol.MIEMBRO, usuario_id: int = 7) -> Actor:
    return Actor(usuario_id=usuario_id, rol=rol)


class Mundo:
    def __init__(self):
        self.movimientos = MovimientoCommandRepositoryFake()
        self.cuentas = CuentaCommandRepositoryFake((HOGAR, 10), (OTRO_HOGAR, 20))
        self.categorias = CategoriaCommandRepositoryFake()
        self.presupuestos = PresupuestoCommandRepositoryFake(self.movimientos, self.categorias)
        self.comercios = ReconocedorComerciosFake(mercadona=100)
        self.auditoria = AuditoriaFake()
        self.eventos = PublicadorEventosFake()
        self.uow = UnidadDeTrabajoFake(
            self.movimientos, self.categorias, self.presupuestos, self.auditoria, self.eventos
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
