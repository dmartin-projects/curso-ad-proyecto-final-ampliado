# finanzas/infrastructure/database/repositories/presupuesto_command_repository_orm.py (módulos 76, 87 y 88)
from core.domain.vo.dinero import Dinero
from core.infrastructure.database.guardado import guardar_fila
from core.infrastructure.signals.red_de_seguridad import en_un_caso_de_uso, publicados_por_caso_de_uso
from finanzas.domain.bo.presupuesto import Presupuesto
from finanzas.domain.exceptions.presupuesto_duplicado_exception import PresupuestoDuplicadoException
from finanzas.domain.exceptions.presupuesto_no_encontrado_exception import PresupuestoNoEncontradoException
from finanzas.domain.repositories.i_presupuesto_command_repository import IPresupuestoCommandRepository
from finanzas.infrastructure.database.mappers.presupuesto_mapper import presupuesto_a_bo, presupuesto_a_modelo
from finanzas.infrastructure.database.models.presupuesto_model import Presupuesto as PresupuestoModel

CAMPOS = ["categoria", "mes", "importe"]  # alerta_enviada, NUNCA aquí: solo con cambiar_alerta()


class PresupuestoCommandRepositoryORM(IPresupuestoCommandRepository):
    errores = {"presupuesto_unico": PresupuestoDuplicadoException}

    def obtener(self, hogar_id: int, presupuesto_id: int) -> Presupuesto:
        fila = PresupuestoModel.objects.filter(hogar_id=hogar_id, pk=presupuesto_id).first()
        if fila is None:
            raise PresupuestoNoEncontradoException()
        return presupuesto_a_bo(fila)

    def guardar(self, presupuesto: Presupuesto) -> None:
        fila = publicados_por_caso_de_uso(presupuesto_a_modelo(presupuesto))
        guardar_fila(fila, CAMPOS, self.errores)
        presupuesto.id = fila.pk

    def eliminar(self, presupuesto: Presupuesto) -> None:
        with en_un_caso_de_uso():  # delete() de un QuerySet: no hay instancia que marcar
            PresupuestoModel.objects.filter(pk=presupuesto.id).delete()

    def con_gastado(self, hogar_id, meses):
        filas = PresupuestoModel.objects.filter(
            hogar_id=hogar_id, mes__in=[m.inicio for m in meses]
        ).con_gastado()  # una Subquery correlacionada para todos (módulo 76)
        return [(presupuesto_a_bo(f), Dinero(f.gastado)) for f in filas]

    def cambiar_alerta(self, presupuesto_id: int, *, de: bool, a: bool) -> bool:
        return bool(PresupuestoModel.objects.filter(pk=presupuesto_id, alerta_enviada=de).update(alerta_enviada=a))
