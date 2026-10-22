# usuarios/infrastructure/messaging/publicador_eventos_django.py — IPublicadorEventos de las cuentas (módulo 88)
from django.db import transaction
from django.utils.module_loading import import_string

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from usuarios.domain.events.recuperacion_pedida_event import RecuperacionPedidaEvent
from usuarios.domain.events.registro_con_cuenta_activa_event import RegistroConCuentaActivaEvent
from usuarios.domain.events.registro_por_completar_event import RegistroPorCompletarEvent

# Las tareas de django.tasks por su ruta estable (la que guarda la cola): el publicador no importa tasks/
COMPLETAR = "usuarios.tasks.enviar_email_completar_registro"
CUENTA_EXISTENTE = "usuarios.tasks.enviar_email_cuenta_existente"
RECUPERACION = "usuarios.tasks.enviar_email_recuperacion"


class PublicadorEventosDjango(IPublicadorEventos):
    def publicar(self, *eventos: object) -> None:
        for evento in eventos:
            match evento:
                case RegistroPorCompletarEvent(usuario_id=u, enlace=enlace):
                    transaction.on_commit(lambda u=u, enlace=enlace: import_string(COMPLETAR).enqueue(u, enlace))
                case RegistroConCuentaActivaEvent(usuario_id=u, enlace=enlace):
                    transaction.on_commit(lambda u=u, enlace=enlace: import_string(CUENTA_EXISTENTE).enqueue(u, enlace))
                case RecuperacionPedidaEvent(usuario_id=u, enlace=enlace):
                    transaction.on_commit(lambda u=u, enlace=enlace: import_string(RECUPERACION).enqueue(u, enlace))
                case _:
                    raise TypeError(f"Evento sin traducción: {evento!r}")
