# informes/infrastructure/messaging/publicador_eventos_django.py — IPublicadorEventos de los informes (módulos 78 y 88)
from celery import current_app
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils.module_loading import import_string

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from informes.domain.events.informe_generado_event import InformeGeneradoEvent
from informes.domain.events.informe_pedido_event import InformePedidoEvent
from informes.infrastructure.database.models.informe_mensual_model import InformeMensual as InformeMensualModel
from informes.infrastructure.database.repositories.informe_query_service_orm import InformeQueryServiceORM
from informes.infrastructure.signals import informes_signals

# Las tareas por su nombre (Celery) y por su ruta estable (django.tasks): el publicador no importa tasks/
GENERAR = "informes.tasks.generar_informe"
ENVIAR = "informes.tasks.enviar_informe"


def _generado(e: InformeGeneradoEvent) -> None:
    if e.archivo_anterior:
        default_storage.delete(e.archivo_anterior)  # el PDF reemplazado, solo si el nuevo ya está guardado
    informe = InformeMensualModel.objects.select_related("hogar").get(pk=e.informe_id)
    informes_signals.informe_generado.send(sender=InformeMensualModel, informe=informe, enviar=e.enviar)
    if e.enviar:
        for usuario_id in InformeQueryServiceORM().destinatarios(
            e.informe_id
        ):  # un email por destinatario, con reintento independiente
            import_string(ENVIAR).enqueue(e.informe_id, usuario_id)


class PublicadorEventosDjango(IPublicadorEventos):
    def publicar(self, *eventos: object) -> None:
        for evento in eventos:
            match evento:
                case InformePedidoEvent(hogar_id=h, mes=mes, usuario_id=u, enviar=enviar):
                    transaction.on_commit(
                        lambda h=h, mes=mes, u=u, enviar=enviar: current_app.tasks[GENERAR].delay(
                            h, mes.inicio.isoformat(), u, enviar
                        )
                    )
                case InformeGeneradoEvent():
                    transaction.on_commit(lambda e=evento: _generado(e))
                case _:
                    raise TypeError(f"Evento sin traducción: {evento!r}")
