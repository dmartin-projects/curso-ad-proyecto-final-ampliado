# finanzas/application/apuntar_movimientos_use_case/apuntar_movimientos_use_case.py — lo que apuntan los procesos: tickets, extractos, el seed (módulo 88)
#
# Tickets e importaciones no crean movimientos ni buscan comercios: se lo piden a finanzas. Este use case es la
# puerta de entrada de los procesos, como RegistrarMovimientoUseCase lo es de una persona.
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from core.domain.services.normalizacion import normalizar
from core.domain.vo.dinero import Dinero
from finanzas.application.apuntar_movimientos_use_case.dtos.apuntar_movimientos_input_dto import (
    ApuntarMovimientosInputDTO,
)
from finanzas.application.apuntar_movimientos_use_case.dtos.movimiento_apuntado_input_dto import (
    MovimientoApuntadoInputDTO,
)
from finanzas.application.apuntar_movimientos_use_case.i_apuntar_movimientos_use_case import IApuntarMovimientosUseCase
from finanzas.application.ports.i_reconocedor_comercios import IReconocedorComercios
from finanzas.application.shared.autorizacion_por_hogar import exigir_categoria, exigir_cuenta
from finanzas.domain.bo.movimiento import Movimiento
from finanzas.domain.events.movimientos_apuntados_event import MovimientosApuntadosEvent
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


class ApuntarMovimientosUseCase(IApuntarMovimientosUseCase):
    """Movimientos que trae un proceso, uno o quinientos: un INSERT.

    Sin la regla de la fecha futura (el banco y el ticket traen la fecha que traen: es de Movimiento.registrar(),
    "una persona apunta un gasto") y sin auditoría (no los apunta una persona: el ticket o la importación ya dicen
    de dónde salen). El comercio y la categoría, como siempre: se reconocen una vez por concepto (en un extracto,
    "MERCADONA" se repite mucho).
    """

    rol_minimo = Rol.MIEMBRO

    def __init__(
        self,
        *,
        movimientos: IMovimientoCommandRepository,
        cuentas: ICuentaCommandRepository,
        categorias: ICategoriaCommandRepository,
        comercios: IReconocedorComercios,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.movimientos, self.cuentas, self.categorias, self.comercios = movimientos, cuentas, categorias, comercios
        self.eventos, self.uow = eventos, uow

    def _clasificador(self, hogar_id: int):
        vistos: dict[tuple, tuple[int | None, str | None, int | None]] = {}

        def clasificar(a: MovimientoApuntadoInputDTO) -> tuple[int | None, str | None, int | None]:
            """(comercio_id, su nombre comercial si se ha reconocido por el nombre, categoria_id), una vez por texto."""
            if a.comercio_id is not None:  # ya resuelto: solo falta, quizá, la categoría
                return (
                    a.comercio_id,
                    None,
                    self.comercios.categoria_habitual(hogar_id, a.comercio_id, a.categoria_sugerida),
                )
            texto = a.comercio or a.concepto
            clave = (bool(a.comercio), normalizar(texto), a.nif, a.categoria_sugerida)
            if clave not in vistos:
                comercio_id, nombre = None, None
                if a.comercio:
                    comercio_id, nombre = self.comercios.reconocer_o_crear(a.comercio, a.nif) or (None, None)
                else:
                    comercio_id = self.comercios.reconocer(a.concepto)
                vistos[clave] = (
                    comercio_id,
                    nombre,
                    self.comercios.categoria_habitual(hogar_id, comercio_id, a.categoria_sugerida),
                )
            return vistos[clave]

        return clasificar

    def ejecutar(self, entrada: ApuntarMovimientosInputDTO) -> list[int]:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            exigir_cuenta(self.cuentas, entrada.hogar_id, entrada.cuenta_id)
            for categoria_id in {a.categoria_id for a in entrada.movimientos} - {None}:
                exigir_categoria(self.categorias, entrada.hogar_id, categoria_id, "categoria")
            clasificar = self._clasificador(entrada.hogar_id)
            nuevos = []
            for a in entrada.movimientos:
                if a.comercio_id is not None and a.categoria_id is not None:
                    comercio_id, nombre, categoria_id = a.comercio_id, None, a.categoria_id  # nada que reconocer
                else:
                    comercio_id, nombre, habitual = clasificar(a)
                    categoria_id = a.categoria_id if a.categoria_id is not None else habitual
                nuevos.append(
                    Movimiento(
                        hogar_id=entrada.hogar_id,
                        cuenta_id=entrada.cuenta_id,
                        fecha=a.fecha,
                        importe=Dinero(a.importe),
                        concepto=nombre
                        or a.concepto,  # el ticket: su nombre comercial ("Mercadona", no "MERCADONA SA")
                        comercio_id=comercio_id,
                        categoria_id=categoria_id,
                        origen=entrada.origen,
                        revisado=a.revisado,
                        creado_por_id=entrada.actor.usuario_id,
                        huella=a.huella,
                    )
                )
            self.movimientos.crear_varios(nuevos)
            if nuevos:
                ids = tuple(m.id for m in nuevos)
                self.eventos.publicar(
                    MovimientosApuntadosEvent(entrada.hogar_id, ids, frozenset(m.mes for m in nuevos))
                )
        return [m.id for m in nuevos]
