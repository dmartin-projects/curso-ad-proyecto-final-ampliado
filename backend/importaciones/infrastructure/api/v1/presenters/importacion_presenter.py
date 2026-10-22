# importaciones/infrastructure/api/v1/presenters/importacion_presenter.py — de los OutputDTOs a lo que leen los serializers (módulo 88)
#
# Los serializers son los de siempre (ModelSerializers: el esquema OpenAPI sale de ellos) y leen atributos con la
# forma del modelo: cuenta.pk, coincide_con.pk, coincide_con.concepto. Los presenters les dan esa forma.
from types import SimpleNamespace

from importaciones.application.shared.dtos.fila_listada_output_dto import FilaListadaOutputDTO
from importaciones.application.shared.dtos.importacion_listada_output_dto import ImportacionListadaOutputDTO


def presentar(i: ImportacionListadaOutputDTO) -> SimpleNamespace:
    campos = {c: getattr(i, c) for c in i.__dataclass_fields__ if c != "cuenta_id"}
    return SimpleNamespace(pk=i.id, cuenta=SimpleNamespace(pk=i.cuenta_id), **campos)


def presentar_fila(f: FilaListadaOutputDTO) -> SimpleNamespace:
    coincide = None
    if f.coincide_con_id is not None:
        coincide = SimpleNamespace(pk=f.coincide_con_id, concepto=f.coincide_con_concepto)
    return SimpleNamespace(
        pk=f.id,
        id=f.id,
        numero=f.numero,
        fecha=f.fecha,
        concepto=f.concepto,
        importe=f.importe,
        accion=f.accion,
        coincide_con=coincide,
        movimiento=None if f.movimiento_id is None else SimpleNamespace(pk=f.movimiento_id),
    )
