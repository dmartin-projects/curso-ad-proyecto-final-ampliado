# informes/tests/fakes/informe_command_repository_fake.py — IInformeCommandRepository en memoria (módulo 88)
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia
from informes.domain.repositories.i_informe_command_repository import IInformeCommandRepository


class InformeCommandRepositoryFake(AlmacenEnMemoria, IInformeCommandRepository):
    def del_mes(self, hogar_id, mes):
        return next((copia(i) for i in self._datos.values() if (i.hogar_id, i.mes) == (hogar_id, mes)), None)

    def guardar(self, informe, pdf):
        anterior = self._datos[informe.id].archivo if informe.id in self._datos else None
        self._asignar_id(informe)
        informe.archivo = f"informes/{informe.hogar_id}/{informe.mes}-{len(self._datos) + 1}.pdf"
        self._datos[informe.id] = copia(informe)
        return anterior
