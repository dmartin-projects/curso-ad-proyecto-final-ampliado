# asistente/infrastructure/api/v1/views/preguntar_view.py — una pregunta, con la respuesta en streaming (módulo 97)
"""POST /api/v1/hogares/{h}/asistente/conversaciones/{c}/preguntar/  (JSON o multipart: texto [+ archivo])
→ 200 text/event-stream: inicio, tool, texto, grafico, archivo, propuesta, titulo, fin | error

- SSE y no WebSocket: es una respuesta HTTP normal que llega por partes y en un solo sentido. Pasa por Vercel y Caddy
  como el resto de la API, se autentica igual (el JWT del interceptor de Angular) y no necesita Channels.
- La vista es de DRF (síncrona): autentica, comprueba el rol, valida y responde 400/404 ANTES de empezar, porque una vez
  enviado el 200 ya no se puede cambiar el código. Lo que devuelve es una StreamingHttpResponse con un generador
  asíncrono, que Django sirve desde el bucle de ASGI.
"""

from django.http import StreamingHttpResponse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from asistente.application.chat.adjunto import MAX_BYTES, TIPOS, Adjunto
from asistente.application.obtener_conversacion_use_case.dtos.obtener_conversacion_input_dto import (
    ObtenerConversacionInputDTO,
)
from asistente.application.responder_pregunta_use_case.dtos.responder_pregunta_input_dto import (
    ResponderPreguntaInputDTO,
)
from asistente.domain.exceptions.adjunto_no_valido_exception import AdjuntoNoValidoException
from asistente.infrastructure import container
from asistente.infrastructure.api.v1.serializers.pregunta_serializer import PreguntaSerializer
from asistente.infrastructure.api.v1.streaming.transmitir import transmitir
from asistente.infrastructure.api.v1.views.sin_negociacion import SinNegociacion
from asistente.infrastructure.database.models.conversacion_model import Conversacion as ConversacionModel
from core.infrastructure.api.views import consultas
from hogares.infrastructure.api.base.hogar_desde_url_mixin import HogarDesdeUrlMixin
from hogares.infrastructure.api.base.rol_en_hogar import RolEnHogar
from hogares.models import Membresia


class PreguntarView(HogarDesdeUrlMixin, APIView):
    """Una pregunta en una conversación. La respuesta, en streaming (Server-Sent Events): inicio, tool, texto,
    grafico, archivo, propuesta, titulo y fin (o error)."""

    permission_classes = [IsAuthenticated, RolEnHogar]
    roles_por_metodo = {"POST": Membresia.Rol.LECTOR}  # el agente solo lee; cambiar algo lo decide quien confirma
    parser_classes = [JSONParser, MultiPartParser]
    content_negotiation_class = SinNegociacion
    throttle_scope = "asistente"  # cada pregunta cuesta tokens: un límite por persona (las cuotas, módulo 98)

    @extend_schema(
        request={"application/json": PreguntaSerializer, "multipart/form-data": PreguntaSerializer},
        responses={(200, "text/event-stream"): OpenApiResponse(description="Los pasos de la respuesta (SSE)")},
    )
    def post(self, request, hogar_pk: int, pk: int, **kwargs):
        datos = PreguntaSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        hogar_id, actor = self.hogar.pk, self.actor
        # La conversación, de quien pregunta: el 404, ahora (después del 200 ya no se puede)
        if container.obtener_conversacion().ejecutar(ObtenerConversacionInputDTO(hogar_id, actor, pk)) is None:
            raise consultas.no_encontrado(ConversacionModel)
        adjunto = self._adjunto(datos.validated_data.get("archivo"))
        texto = datos.validated_data["texto"]

        def trabajo(emisor):
            entrada = ResponderPreguntaInputDTO(hogar_id, actor, pk, texto, emisor, adjunto)
            container.responder_pregunta().ejecutar(entrada)

        respuesta = StreamingHttpResponse(transmitir(trabajo), content_type="text/event-stream; charset=utf-8")
        respuesta["Cache-Control"] = "no-cache"  # ni el navegador ni un proxy deben guardarla ni agruparla
        respuesta["X-Accel-Buffering"] = "no"  # nginx (y los proxies que lo imitan): enviar cada trozo, no acumular
        return respuesta

    @staticmethod
    def _adjunto(archivo) -> Adjunto | None:
        if archivo is None:
            return None
        if archivo.content_type not in TIPOS or archivo.size > MAX_BYTES:
            raise ValidationError({"archivo": [AdjuntoNoValidoException.mensaje]})
        return Adjunto(archivo.name, archivo.content_type, archivo.read())
