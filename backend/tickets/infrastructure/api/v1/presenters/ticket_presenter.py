# tickets/infrastructure/api/v1/presenters/ticket_presenter.py — del OutputDTO a lo que lee el serializer (módulo 88)
#
# TicketSerializer es el de siempre (un ModelSerializer: el esquema OpenAPI sale de él) y lee atributos con la forma
# del modelo: cuenta.pk, lineas (una lista), movimiento.categoria.pk. El presenter le da esa forma.
from types import SimpleNamespace

from tickets.application.shared.dtos.ticket_listado_output_dto import TicketListadoOutputDTO


def presentar(t: TicketListadoOutputDTO) -> SimpleNamespace:
    g = t.gasto
    return SimpleNamespace(
        pk=t.id,
        id=t.id,
        estado=t.estado,
        cuenta=SimpleNamespace(pk=t.cuenta_id),
        nombre_original=t.nombre_original,
        tipo=t.tipo,
        confianza=t.confianza,
        error=t.error,
        datos_ia=t.datos_ia,
        intentos=t.intentos,
        lineas=[_linea(li) for li in t.lineas],
        movimiento=None
        if g is None
        else SimpleNamespace(
            pk=g.id,
            id=g.id,
            fecha=g.fecha,
            importe=g.importe,
            concepto=g.concepto,
            categoria=None if g.categoria_id is None else SimpleNamespace(pk=g.categoria_id),
            revisado=g.revisado,
        ),
        creado=t.creado,
        procesado_en=t.procesado_en,
    )


def _linea(li) -> SimpleNamespace:
    return SimpleNamespace(
        orden=li.orden,
        descripcion=li.descripcion,
        cantidad=li.cantidad,
        precio_unitario=li.precio_unitario,
        importe=li.importe,
    )
