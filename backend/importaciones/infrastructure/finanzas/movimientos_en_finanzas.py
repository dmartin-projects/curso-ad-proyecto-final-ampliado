# importaciones/infrastructure/finanzas/movimientos_en_finanzas.py — IMovimientos con finanzas (módulo 88)
#
# Leer, con los query services de finanzas (el lado de lectura se puede compartir); escribir, SOLO con sus use cases,
# pedidos a su contenedor. Es la única pieza de importaciones que conoce finanzas por dentro (anti-corruption layer).
from finanzas.application.apuntar_movimientos_use_case.dtos.apuntar_movimientos_input_dto import (
    ApuntarMovimientosInputDTO,
)
from finanzas.application.apuntar_movimientos_use_case.dtos.movimiento_apuntado_input_dto import (
    MovimientoApuntadoInputDTO,
)
from finanzas.application.conciliar_movimientos_use_case.dtos.conciliar_movimientos_input_dto import (
    ConciliarMovimientosInputDTO,
)
from finanzas.application.desconciliar_movimientos_use_case.dtos.desconciliar_movimientos_input_dto import (
    DesconciliarMovimientosInputDTO,
)
from finanzas.application.eliminar_movimientos_use_case.dtos.eliminar_movimientos_input_dto import (
    EliminarMovimientosInputDTO,
)
from finanzas.domain.enums.origen import Origen
from finanzas.infrastructure import container as finanzas
from finanzas.infrastructure.database.repositories.cuenta_query_service_orm import CuentaQueryServiceORM
from finanzas.infrastructure.database.repositories.movimiento_query_service_orm import MovimientoQueryServiceORM
from importaciones.application.ports.i_movimientos import IMovimientos
from importaciones.domain.vo.candidato import Candidato


class MovimientosEnFinanzas(IMovimientos):
    def cuenta_del_hogar(self, hogar_id, cuenta_id):
        return CuentaQueryServiceORM().existe(hogar_id, cuenta_id)

    def huellas_existentes(self, cuenta_id, huellas):
        return MovimientoQueryServiceORM().huellas_existentes(cuenta_id, huellas)

    def candidatos(self, cuenta_id, desde, hasta):
        sin_conciliar = MovimientoQueryServiceORM().sin_conciliar(cuenta_id, desde, hasta)
        return [Candidato(m.id, m.fecha, m.importe) for m in sin_conciliar]

    def apuntar(self, *, hogar_id, actor, cuenta_id, filas):
        apuntados = tuple(MovimientoApuntadoInputDTO(f.fecha, f.importe, f.concepto, huella=f.huella) for f in filas)
        if not apuntados:
            return []
        entrada = ApuntarMovimientosInputDTO(hogar_id, actor, cuenta_id, Origen.EXTRACTO, apuntados)
        return finanzas.apuntar_movimientos().ejecutar(entrada)

    def conciliar(self, *, hogar_id, actor, huellas):
        if not huellas:
            return set()
        return set(finanzas.conciliar_movimientos().ejecutar(ConciliarMovimientosInputDTO(hogar_id, actor, huellas)))

    def eliminar(self, *, hogar_id, actor, ids):
        finanzas.eliminar_movimientos().ejecutar(EliminarMovimientosInputDTO(hogar_id, actor, tuple(ids)))

    def desconciliar(self, *, hogar_id, actor, ids):
        finanzas.desconciliar_movimientos().ejecutar(DesconciliarMovimientosInputDTO(hogar_id, actor, tuple(ids)))
