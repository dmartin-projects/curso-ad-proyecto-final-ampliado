# notificaciones/infrastructure/websocket/consumers.py — adapter de entrada: el WebSocket (módulos 76 y 88)
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from notificaciones.application.obtener_estado_inicial_use_case.dtos.obtener_estado_inicial_input_dto import (
    ObtenerEstadoInicialInputDTO,
)
from notificaciones.infrastructure import container
from notificaciones.infrastructure.realtime import grupos


class NotificacionesConsumer(AsyncJsonWebsocketConsumer):
    """Un socket por pestaña. Recibe: notificaciones del usuario y eventos de sus hogares."""

    async def connect(self):
        usuario = self.scope["user"]
        if not usuario.is_authenticated:
            # Aceptar y cerrar: si se cierra antes de accept(), el navegador solo ve un handshake fallido
            # (código 1006) y no puede distinguir "ticket caducado" de "servidor caído".
            await self.accept()
            await self.close(code=4401)
            return
        estado = await self._estado_inicial(usuario.pk)
        self.grupos = [grupos.de_usuario(usuario.pk), *(grupos.de_hogar(h) for h in estado.hogares)]
        for grupo in self.grupos:
            await self.channel_layer.group_add(grupo, self.channel_name)
        await self.accept()
        await self.send_json({"tipo": "conectado", "no_leidas": estado.no_leidas})

    async def disconnect(self, code):
        for grupo in getattr(self, "grupos", []):
            await self.channel_layer.group_discard(grupo, self.channel_name)

    async def receive_json(self, contenido, **kwargs):
        if contenido.get("accion") == "ping":  # latido del cliente: mantiene viva la conexión tras proxies
            await self.send_json({"tipo": "pong"})

    # ── Mensajes de la channel layer: "type" → método ──
    async def notificacion_nueva(self, evento):
        await self.send_json({"tipo": "notificacion", "datos": evento["datos"]})

    async def hogar_evento(self, evento):
        await self.send_json(
            {"tipo": "evento", "evento": evento["evento"], "hogar": evento["hogar"], "datos": evento["datos"]}
        )

    async def grupos_cambiados(self, evento):
        await self.close(code=4000)  # el cliente reconecta y recibe los grupos actualizados

    @database_sync_to_async
    def _estado_inicial(self, usuario_id):
        return container.obtener_estado_inicial().ejecutar(ObtenerEstadoInicialInputDTO(usuario_id))
