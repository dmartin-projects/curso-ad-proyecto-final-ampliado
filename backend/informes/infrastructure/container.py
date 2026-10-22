# informes/infrastructure/container.py — composition root de los informes (módulo 88)
from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango
from informes.application.generar_informe_use_case.generar_informe_use_case import GenerarInformeUseCase
from informes.application.generar_informe_use_case.i_generar_informe_use_case import IGenerarInformeUseCase
from informes.application.listar_hogares_sin_informe_use_case.i_listar_hogares_sin_informe_use_case import (
    IListarHogaresSinInformeUseCase,
)
from informes.application.listar_hogares_sin_informe_use_case.listar_hogares_sin_informe_use_case import (
    ListarHogaresSinInformeUseCase,
)
from informes.application.listar_informes_use_case.i_listar_informes_use_case import IListarInformesUseCase
from informes.application.listar_informes_use_case.listar_informes_use_case import ListarInformesUseCase
from informes.application.obtener_informe_use_case.i_obtener_informe_use_case import IObtenerInformeUseCase
from informes.application.obtener_informe_use_case.obtener_informe_use_case import ObtenerInformeUseCase
from informes.application.pedir_informe_use_case.i_pedir_informe_use_case import IPedirInformeUseCase
from informes.application.pedir_informe_use_case.pedir_informe_use_case import PedirInformeUseCase
from informes.infrastructure.database.repositories.informe_command_repository_orm import InformeCommandRepositoryORM
from informes.infrastructure.database.repositories.informe_query_service_orm import InformeQueryServiceORM
from informes.infrastructure.messaging.publicador_eventos_django import PublicadorEventosDjango
from informes.infrastructure.pdf.maquetador_weasyprint import MaquetadorWeasyPrint


def pedir_informe() -> IPedirInformeUseCase:
    return PedirInformeUseCase(eventos=PublicadorEventosDjango(), uow=UnidadDeTrabajoDjango(), reloj=RelojDjango())


def generar_informe() -> IGenerarInformeUseCase:
    return GenerarInformeUseCase(
        informes=InformeCommandRepositoryORM(),
        maquetador=MaquetadorWeasyPrint(),
        eventos=PublicadorEventosDjango(),
        uow=UnidadDeTrabajoDjango(),
    )


# ── Lectura ──
def listar_informes() -> IListarInformesUseCase:
    return ListarInformesUseCase(informes=InformeQueryServiceORM())


def obtener_informe() -> IObtenerInformeUseCase:
    return ObtenerInformeUseCase(informes=InformeQueryServiceORM())


def listar_hogares_sin_informe() -> IListarHogaresSinInformeUseCase:
    return ListarHogaresSinInformeUseCase(informes=InformeQueryServiceORM())
