# finanzas/infrastructure/database/mappers/movimiento_mapper.py — BO ↔ fila (módulo 87)
#
# Explícito y aburrido, a propósito: se lee en diez segundos y es el único sitio donde Django y el dominio se tocan.
# En infraestructura, el modelo se importa como MovimientoModel: así no se confunde con el BO Movimiento.
from core.domain.vo.dinero import Dinero
from finanzas.domain.bo.movimiento import Movimiento
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel


def movimiento_a_bo(fila: MovimientoModel) -> Movimiento:
    return Movimiento(
        id=fila.pk,
        hogar_id=fila.hogar_id,
        cuenta_id=fila.cuenta_id,
        fecha=fila.fecha,
        importe=Dinero(fila.importe),
        concepto=fila.concepto,
        categoria_id=fila.categoria_id,
        comercio_id=fila.comercio_id,
        etiquetas=list(fila.etiquetas),
        notas=fila.notas,
        origen=fila.origen,
        revisado=fila.revisado,
        creado_por_id=fila.creado_por_id,
    )


def movimiento_a_modelo(m: Movimiento) -> MovimientoModel:
    return MovimientoModel(
        pk=m.id,
        hogar_id=m.hogar_id,
        cuenta_id=m.cuenta_id,
        fecha=m.fecha,
        importe=m.importe.cantidad,
        concepto=m.concepto,
        categoria_id=m.categoria_id,
        comercio_id=m.comercio_id,
        etiquetas=list(m.etiquetas),
        notas=m.notas,
        origen=str(m.origen),
        revisado=m.revisado,
        creado_por_id=m.creado_por_id,
    )
