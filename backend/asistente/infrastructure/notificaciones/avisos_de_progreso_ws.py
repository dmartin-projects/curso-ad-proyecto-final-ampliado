# asistente/infrastructure/notificaciones/avisos_de_progreso_ws.py — IAvisosDeProgreso con el WebSocket (módulo 105)
#
# Anti-corruption layer hacia notificaciones, la app dueña del WebSocket (módulo 76): un evento a los sockets de esa
# persona, con la forma de los eventos de hogar que la SPA ya escucha.
from asistente.application.ports.i_avisos_de_progreso import IAvisosDeProgreso
from notificaciones.infrastructure import container as notificaciones

EVENTO = "asistente.analisis"


class AvisosDeProgresoWS(IAvisosDeProgreso):
    def avisar(self, usuario_id, hogar_id, tarea, datos):
        notificaciones.emitir_evento_a_usuario(usuario_id, hogar_id, EVENTO, {"tarea": tarea, **datos})
