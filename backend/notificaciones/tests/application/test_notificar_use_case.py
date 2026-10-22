"""NotificarUseCase con fakes (módulo 88): cada persona en su idioma, sin Django."""

from decimal import Decimal

from core.tests.fakes.publicador_eventos_fake import PublicadorEventosFake
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake
from notificaciones.application.notificar_use_case.dtos.notificar_input_dto import NotificarInputDTO
from notificaciones.application.notificar_use_case.notificar_use_case import NotificarUseCase
from notificaciones.domain.enums.tipo_notificacion import TipoNotificacion
from notificaciones.domain.events.notificaciones_creadas_event import NotificacionesCreadasEvent
from notificaciones.tests.fakes.destinatarios_fake import DestinatariosFake
from notificaciones.tests.fakes.notificacion_command_repository_fake import NotificacionCommandRepositoryFake
from notificaciones.tests.fakes.traductor_fake import TraductorFake

TITULO = {"es": "Presupuesto de %(categoria)s superado", "en": "%(categoria)s budget exceeded"}


def test_cada_miembro_en_su_idioma_y_un_aviso_al_confirmar():
    repo, eventos = NotificacionCommandRepositoryFake(), PublicadorEventosFake()
    notificar = NotificarUseCase(
        notificaciones=repo,
        destinatarios=DestinatariosFake({1: "es", 2: "en", 3: "es"}, {9: [1, 2]}),
        traductor=TraductorFake(),
        eventos=eventos,
        uow=UnidadDeTrabajoFake(repo, eventos),
    )
    nuevas = notificar.ejecutar(
        NotificarInputDTO(
            TipoNotificacion.PRESUPUESTO_SUPERADO,
            TITULO,
            contexto={"categoria": "Súper", "gastado": Decimal("110")},
            miembros_de=9,
            hogar_id=9,
            email=True,
        )  # fmt: skip
    )
    assert [(n.usuario_id, n.titulo) for n in nuevas] == [
        (1, "Presupuesto de Súper superado"),
        (2, "Súper budget exceeded"),
    ]
    assert nuevas[0].datos == {"categoria": "Súper", "gastado": "110"}  # como texto: van a un JSONField
    assert eventos.publicados == [NotificacionesCreadasEvent((1, 2), True)]


def test_un_titulo_largo_se_recorta_y_sin_destinatarios_no_se_publica_nada():
    repo, eventos = NotificacionCommandRepositoryFake(), PublicadorEventosFake()
    notificar = NotificarUseCase(notificaciones=repo, destinatarios=DestinatariosFake({1: "es"}, {}),
                          traductor=TraductorFake(), eventos=eventos, uow=UnidadDeTrabajoFake(repo, eventos))  # fmt: skip
    [n] = notificar.ejecutar(NotificarInputDTO(TipoNotificacion.INFORME_LISTO, {"es": "x" * 300}, usuarios=(1,)))
    assert len(n.titulo) == 150
    assert notificar.ejecutar(NotificarInputDTO(TipoNotificacion.INFORME_LISTO, {"es": "x"}, miembros_de=5)) == []
    assert len(eventos.publicados) == 1
