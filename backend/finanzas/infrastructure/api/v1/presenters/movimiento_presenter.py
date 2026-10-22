# finanzas/infrastructure/api/v1/presenters/movimiento_presenter.py — del OutputDTO a lo que lee el serializer
# (módulo 87)
#
# MovimientoSerializer es el de siempre (la entrada y el esquema OpenAPI salen de él) y, para escribir la response,
# lee atributos con la forma del modelo: `cuenta.pk`, `categoria.nombre`, `comercio.id`. El presenter le da esa forma a
# partir del OutputDTO plano del use case de consulta. Mismo serializer, mismo JSON.
from types import SimpleNamespace

from finanzas.application.shared.dtos.movimiento_listado_output_dto import MovimientoListadoOutputDTO


def presentar(m: MovimientoListadoOutputDTO) -> SimpleNamespace:
    presentado = SimpleNamespace(
        id=m.id,
        fecha=m.fecha,
        importe=m.importe,
        concepto=m.concepto,
        cuenta=SimpleNamespace(pk=m.cuenta_id, nombre=m.cuenta_nombre),
        categoria=SimpleNamespace(pk=m.categoria_id, nombre=m.categoria_nombre, color=m.categoria_color)
        if m.categoria_id is not None
        else None,
        comercio=SimpleNamespace(pk=m.comercio_id, id=m.comercio_id, nombre=m.comercio_nombre)
        if m.comercio_id is not None
        else None,
        etiquetas=list(m.etiquetas),
        notas=m.notas,
        origen=m.origen,
        revisado=m.revisado,
        creado=m.creado,
    )
    if m.num_adjuntos is not None:  # sin contar, el serializer pone su valor por defecto, como siempre
        presentado.num_adjuntos = m.num_adjuntos
    return presentado
