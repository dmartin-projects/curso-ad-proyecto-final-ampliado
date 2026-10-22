# finanzas/infrastructure/database/repositories/movimiento_command_repository_orm.py (módulo 87)
#
# El lado de escritura con el ORM: traduce entre el BO y su fila (mappers/) y marca lo que guarda para que los
# receivers de red de seguridad no publiquen otra vez lo que ya publica el use case.
from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from core.infrastructure.database.guardado import guardar_fila
from core.infrastructure.signals.red_de_seguridad import publicados_por_caso_de_uso
from finanzas.domain.bo.movimiento import Movimiento
from finanzas.domain.exceptions.movimiento_no_encontrado_exception import MovimientoNoEncontradoException
from finanzas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository
from finanzas.infrastructure.database.mappers.movimiento_mapper import movimiento_a_bo, movimiento_a_modelo
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel

CAMPOS = [
    "cuenta",
    "fecha",
    "importe",
    "concepto",
    "categoria",
    "comercio",
    "etiquetas",
    "notas",
    "origen",
    "revisado",
]  # en un UPDATE nunca cambian hogar, creado_por ni huella (la de las importaciones, módulo 75)


def _columnas(cambios: dict) -> dict:
    return {campo: v.cantidad if isinstance(v, Dinero) else v for campo, v in cambios.items()}


class MovimientoCommandRepositoryORM(IMovimientoCommandRepository):
    def obtener(self, hogar_id: int, movimiento_id: int) -> Movimiento:
        fila = MovimientoModel.objects.filter(hogar_id=hogar_id, pk=movimiento_id).first()
        if fila is None:
            raise MovimientoNoEncontradoException()
        return movimiento_a_bo(fila)

    def obtener_varios(self, hogar_id, ids):
        filas = MovimientoModel.objects.filter(hogar_id=hogar_id, pk__in=list(ids)).order_by("pk")
        return [movimiento_a_bo(f) for f in filas]

    def guardar(self, movimiento: Movimiento) -> None:
        fila = publicados_por_caso_de_uso(movimiento_a_modelo(movimiento))  # los receivers no publican: el use case sí
        guardar_fila(fila, CAMPOS, {})
        movimiento.id = fila.pk

    def eliminar(self, movimiento: Movimiento) -> None:
        # delete() de una instancia: Django borra en cascada sus adjuntos (GenericRelation) como siempre
        publicados_por_caso_de_uso(MovimientoModel(pk=movimiento.id, hogar_id=movimiento.hogar_id)).delete()

    def actualizar_en_bloque(self, hogar_id, ids, cambios):
        filas = list(MovimientoModel.objects.filter(hogar_id=hogar_id, pk__in=list(ids)).values_list("pk", "fecha"))
        afectados = sorted(pk for pk, _ in filas)
        if afectados:
            MovimientoModel.objects.filter(pk__in=afectados).update(**_columnas(cambios))  # un UPDATE, sin señales
        return afectados, {Mes.de(fecha) for _, fecha in filas}
