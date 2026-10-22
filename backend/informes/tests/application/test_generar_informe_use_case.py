"""GenerarInformeUseCase con fakes (módulo 88)."""

from core.domain.vo.mes import Mes
from informes.application.generar_informe_use_case.dtos.generar_informe_input_dto import GenerarInformeInputDTO
from informes.domain.events.informe_generado_event import InformeGeneradoEvent

OCT = Mes(2026, 10)


def test_regenerar_reutiliza_el_informe_y_devuelve_el_archivo_viejo(mundo):
    _, generar, informes, eventos = mundo
    primero = generar.ejecutar(GenerarInformeInputDTO(1, OCT, enviar=False))
    segundo = generar.ejecutar(GenerarInformeInputDTO(1, OCT, usuario_id=7))
    assert segundo.id == primero.id and segundo.archivo != primero.archivo and segundo.tamano > 0
    assert not segundo.automatico and len(informes.todos()) == 1
    assert eventos.publicados == [
        InformeGeneradoEvent(primero.id, False, None),
        InformeGeneradoEvent(primero.id, True, primero.archivo),
    ]
