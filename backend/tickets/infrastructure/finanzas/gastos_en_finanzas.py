# tickets/infrastructure/finanzas/gastos_en_finanzas.py — IGastos con los use cases de finanzas (módulo 88)
#
# Un adapter hacia OTRA app: traduce lo que los tickets necesitan ("el gasto de este ticket") al idioma de finanzas
# (InputDTOs de sus use cases, pedidos a su contenedor; para leer, sus query services). Es la única pieza de tickets
# que conoce finanzas por dentro: si mañana finanzas cambia un use case, se toca este archivo y nada más
# (anti-corruption layer).
from core.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery
from finanzas.application.apuntar_movimientos_use_case.dtos.apuntar_movimientos_input_dto import (
    ApuntarMovimientosInputDTO,
)
from finanzas.application.apuntar_movimientos_use_case.dtos.movimiento_apuntado_input_dto import (
    MovimientoApuntadoInputDTO,
)
from finanzas.application.descartar_propuestos_use_case.dtos.descartar_propuestos_input_dto import (
    DescartarPropuestosInputDTO,
)
from finanzas.application.modificar_movimiento_use_case.dtos.modificar_movimiento_input_dto import (
    ModificarMovimientoInputDTO,
)
from finanzas.application.registrar_movimiento_use_case.dtos.registrar_movimiento_input_dto import (
    RegistrarMovimientoInputDTO,
)
from finanzas.domain.enums.origen import Origen
from finanzas.infrastructure import container as finanzas
from finanzas.infrastructure.database.repositories.categoria_query_service_orm import CategoriaQueryServiceORM
from finanzas.infrastructure.database.repositories.cuenta_query_service_orm import CuentaQueryServiceORM
from tickets.application.ports.i_gastos import IGastos


class GastosEnFinanzas(IGastos):
    def nombres_de_categorias(self, hogar_id: int) -> list[str]:
        return [c.nombre for c in CategoriaQueryServiceORM().listar(ListadoDelHogarQuery(hogar_id))]

    def existe_cuenta(self, hogar_id: int, cuenta_id: int) -> bool:
        return CuentaQueryServiceORM().existe(hogar_id, cuenta_id)

    def apuntar(
        self, *, hogar_id, actor, cuenta_id, fecha, total, concepto, comercio, nif, categoria_sugerida, revisado
    ):
        apuntado = MovimientoApuntadoInputDTO(
            fecha=fecha,
            importe=-total,  # un ticket es un gasto
            concepto=concepto,
            comercio=comercio,
            nif=nif,
            categoria_sugerida=categoria_sugerida,
            revisado=revisado,
        )
        entrada = ApuntarMovimientosInputDTO(hogar_id, actor, cuenta_id, Origen.TICKET, (apuntado,))
        [movimiento_id] = finanzas.apuntar_movimientos().ejecutar(entrada)
        return movimiento_id

    def registrar(self, *, hogar_id, actor, cuenta_id, fecha, total, concepto, categoria_id):
        entrada = RegistrarMovimientoInputDTO(
            hogar_id=hogar_id,
            actor=actor,
            cuenta_id=cuenta_id,
            fecha=fecha,
            importe=-total,
            concepto=concepto,
            categoria_id=categoria_id,
            origen=Origen.TICKET,
        )
        return finanzas.registrar_movimiento().ejecutar(entrada).id

    def corregir(self, *, hogar_id, actor, movimiento_id, fecha, total, concepto, categoria_id):
        cambios = {
            "fecha": fecha,
            "importe": -total,
            "concepto": concepto,
            "categoria_id": categoria_id,
            "revisado": True,
        }
        finanzas.modificar_movimiento().ejecutar(ModificarMovimientoInputDTO(hogar_id, actor, movimiento_id, cambios))

    def descartar(self, *, hogar_id, actor, movimiento_id):
        entrada = DescartarPropuestosInputDTO(hogar_id, actor, (movimiento_id,))
        return bool(finanzas.descartar_propuestos().ejecutar(entrada))
