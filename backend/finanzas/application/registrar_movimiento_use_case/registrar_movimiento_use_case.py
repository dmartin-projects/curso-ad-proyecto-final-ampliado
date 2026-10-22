# finanzas/application/registrar_movimiento_use_case/registrar_movimiento_use_case.py (módulos 87 y 88)
#
# Un use case ORQUESTA: comprueba quién lo pide (autorización por hogar), abre la transacción, construye o carga
# los BOs, les pide que cambien (las reglas son suyas), guarda, audita y publica los eventos, todo dentro de la
# misma transacción. No sabe de HTTP, de serializers, de Celery ni del ORM: solo de interfaces.
from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from core.domain.vo.dinero import Dinero
from finanzas.application.ports.i_reconocedor_comercios import IReconocedorComercios
from finanzas.application.registrar_movimiento_use_case.dtos.registrar_movimiento_input_dto import (
    RegistrarMovimientoInputDTO,
)
from finanzas.application.registrar_movimiento_use_case.i_registrar_movimiento_use_case import (
    IRegistrarMovimientoUseCase,
)
from finanzas.application.shared.autorizacion_por_hogar import exigir_categoria, exigir_cuenta
from finanzas.application.shared.dtos.movimiento_output_dto import MovimientoOutputDTO
from finanzas.domain.bo.movimiento import Movimiento
from finanzas.domain.events.movimiento_registrado_event import MovimientoRegistradoEvent
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository


class RegistrarMovimientoUseCase(IRegistrarMovimientoUseCase):
    rol_minimo = Rol.MIEMBRO

    def __init__(
        self,
        *,
        movimientos: IMovimientoCommandRepository,
        cuentas: ICuentaCommandRepository,
        categorias: ICategoriaCommandRepository,
        comercios: IReconocedorComercios,
        auditoria: IAuditoria,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
        reloj: IReloj,
    ):
        self.movimientos, self.cuentas, self.categorias, self.comercios = movimientos, cuentas, categorias, comercios
        self.auditoria, self.eventos, self.uow, self.reloj = auditoria, eventos, uow, reloj

    def ejecutar(self, entrada: RegistrarMovimientoInputDTO) -> MovimientoOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        movimiento = Movimiento.registrar(  # las reglas, antes de tocar la base de datos
            hoy=self.reloj.hoy(),
            hogar_id=entrada.hogar_id,
            cuenta_id=entrada.cuenta_id,
            fecha=entrada.fecha,
            importe=Dinero(entrada.importe),
            concepto=entrada.concepto,
            categoria_id=entrada.categoria_id,
            etiquetas=entrada.etiquetas,
            notas=entrada.notas,
            revisado=entrada.revisado,
            origen=entrada.origen,
            creado_por_id=entrada.actor.usuario_id,
        )
        with self.uow:  # el movimiento, su auditoría y su evento: todo o nada (módulo 85)
            exigir_cuenta(self.cuentas, entrada.hogar_id, entrada.cuenta_id)
            if entrada.categoria_id is not None:
                exigir_categoria(self.categorias, entrada.hogar_id, entrada.categoria_id, "categoria")
            movimiento.comercio_id = self.comercios.reconocer(movimiento.concepto)
            self.movimientos.guardar(movimiento)
            self.auditoria.registrar(Accion.CREAR, movimiento, entrada.actor.usuario_id)
            self.eventos.publicar(MovimientoRegistradoEvent(movimiento.instantanea()))
        return MovimientoOutputDTO.desde_bo(movimiento)
