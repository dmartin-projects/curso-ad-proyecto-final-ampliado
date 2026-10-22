from datetime import date

import pytest

from core.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from core.tests.fakes.reloj_fake import RelojFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from informes.application.generar_informe_use_case.generar_informe_use_case import GenerarInformeUseCase
from informes.application.pedir_informe_use_case.pedir_informe_use_case import PedirInformeUseCase
from informes.tests.fakes.informe_command_repository_fake import InformeCommandRepositoryFake
from informes.tests.fakes.maquetador_fake import MaquetadorFake


@pytest.fixture
def mundo():
    """Los use cases de los informes con fakes: ni WeasyPrint ni base de datos (módulo 88)."""
    informes, eventos = InformeCommandRepositoryFake(), PublicadorEventosFake()
    uow = UnidadDeTrabajoFake(informes, eventos)
    pedir = PedirInformeUseCase(eventos=eventos, uow=uow, reloj=RelojFake(date(2026, 10, 15)))
    generar = GenerarInformeUseCase(informes=informes, maquetador=MaquetadorFake(), eventos=eventos, uow=uow)
    return pedir, generar, informes, eventos
