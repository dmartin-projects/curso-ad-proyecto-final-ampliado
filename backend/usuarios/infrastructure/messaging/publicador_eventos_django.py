# usuarios/infrastructure/messaging/publicador_eventos_django.py — IPublicadorEventos de las cuentas (módulos 88, 91 y 92)
from django.db import transaction
from django.utils.module_loading import import_string

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from usuarios.domain.events.inicio_desde_dispositivo_nuevo_event import InicioDesdeDispositivoNuevoEvent
from usuarios.domain.events.proveedor_vinculado_event import ProveedorVinculadoEvent
from usuarios.domain.events.recuperacion_pedida_event import RecuperacionPedidaEvent
from usuarios.domain.events.registro_con_cuenta_activa_event import RegistroConCuentaActivaEvent
from usuarios.domain.events.registro_por_completar_event import RegistroPorCompletarEvent
from usuarios.domain.events.seguridad_cambiada_event import SeguridadCambiadaEvent

# Las tareas de django.tasks por su ruta estable (la que guarda la cola): el publicador no importa tasks/
COMPLETAR = "usuarios.tasks.enviar_email_completar_registro"
CUENTA_EXISTENTE = "usuarios.tasks.enviar_email_cuenta_existente"
RECUPERACION = "usuarios.tasks.enviar_email_recuperacion"
VINCULACION = "usuarios.tasks.enviar_aviso_vinculacion"  # módulo 91, ejercicio 2
DISPOSITIVO, SEGURIDAD = "usuarios.tasks.enviar_aviso_dispositivo_nuevo", "usuarios.tasks.enviar_aviso_seguridad"  # 92


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
                case ProveedorVinculadoEvent(usuario_id=u, proveedor=p, cuenta=c):
                    transaction.on_commit(lambda u=u, p=p, c=c: import_string(VINCULACION).enqueue(u, p, c))
                case InicioDesdeDispositivoNuevoEvent(usuario_id=u, dispositivo=d, ip=ip, momento=m):
                    momento = m.isoformat()  # la cola guarda los argumentos en JSON
                    transaction.on_commit(
                        lambda u=u, d=d, ip=ip, momento=momento: import_string(DISPOSITIVO).enqueue(u, d, ip, momento)
                    )
                case SeguridadCambiadaEvent(usuario_id=u, cambio=c, detalle=detalle):
                    transaction.on_commit(lambda u=u, c=c, d=detalle: import_string(SEGURIDAD).enqueue(u, c, d))
                case _:
                    raise TypeError(f"Evento sin traducción: {evento!r}")
