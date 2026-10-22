# tickets/infrastructure/api/v1/views/ticket_viewset.py — adapter de entrada HTTP (módulos 74 y 88)
#
# Escribir: serializer → InputDTO → use case de comando. Leer (listado, detalle, la response de cada acción):
# use case de consulta → OutputDTO → presenter → el mismo serializer de siempre.
from django.core.files.storage import default_storage
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.infrastructure.api.views import consultas
from hogares.infrastructure.api.base.del_hogar_viewset import DelHogarViewSet
from tickets.application.borrar_ticket_use_case.borrar_ticket_use_case import BorrarTicketUseCase
from tickets.application.borrar_ticket_use_case.dtos.borrar_ticket_input_dto import BorrarTicketInputDTO
from tickets.application.confirmar_ticket_use_case.confirmar_ticket_use_case import ConfirmarTicketUseCase
from tickets.application.confirmar_ticket_use_case.dtos.confirmar_ticket_input_dto import ConfirmarTicketInputDTO
from tickets.application.listar_tickets_use_case.dtos.listar_tickets_input_dto import ListarTicketsInputDTO
from tickets.application.obtener_ticket_use_case.dtos.obtener_ticket_input_dto import ObtenerTicketInputDTO
from tickets.application.reprocesar_ticket_use_case.dtos.reprocesar_ticket_input_dto import ReprocesarTicketInputDTO
from tickets.application.reprocesar_ticket_use_case.reprocesar_ticket_use_case import ReprocesarTicketUseCase
from tickets.application.subir_ticket_use_case.dtos.subir_ticket_input_dto import SubirTicketInputDTO
from tickets.application.subir_ticket_use_case.subir_ticket_use_case import SubirTicketUseCase
from tickets.infrastructure import container
from tickets.infrastructure.api.v1.presenters.ticket_presenter import presentar
from tickets.infrastructure.api.v1.serializers.confirmar_ticket_serializer import ConfirmarTicketSerializer
from tickets.infrastructure.api.v1.serializers.reprocesar_ticket_serializer import ReprocesarTicketSerializer
from tickets.infrastructure.api.v1.serializers.subir_ticket_serializer import SubirTicketSerializer
from tickets.infrastructure.api.v1.serializers.ticket_serializer import TicketSerializer
from tickets.infrastructure.api.v1.serializers.url_archivo_serializer import UrlArchivoSerializer
from tickets.infrastructure.database.models.ticket_model import Ticket as TicketModel


class TicketViewSet(DelHogarViewSet):
    """Tickets del hogar. Subir responde 202: el procesado (OCR + IA) ocurre en segundo plano."""

    # Estos atributos son los de siempre: de ellos salen el esquema OpenAPI y la validación de los query params. El
    # QuerySet de DelHogarViewSet solo lo usa get_object() al borrar.
    modelo = TicketModel
    serializer_class = TicketSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]  # un ticket no se edita: se confirma
    filterset_fields = ["estado", "cuenta"]
    search_fields = ["nombre_original", "texto_ocr"]
    ordering_fields = ["creado"]
    ordering = ["-creado"]
    roles_por_accion = {
        "create": SubirTicketUseCase.rol_minimo,
        "destroy": BorrarTicketUseCase.rol_minimo,
        "confirmar": ConfirmarTicketUseCase.rol_minimo,
        "reprocesar": ReprocesarTicketUseCase.rol_minimo,
    }

    def get_serializer_class(self):
        return {
            "create": SubirTicketSerializer,
            "confirmar": ConfirmarTicketSerializer,
            "reprocesar": ReprocesarTicketSerializer,
        }.get(self.action, TicketSerializer)

    def get_throttles(self):
        # límite "subidas" (60/h) solo en lo que dispara OCR + IA, que cuesta CPU y dinero
        self.throttle_scope = "subidas" if self.action in ("create", "reprocesar") else None
        return super().get_throttles()

    def _leer(self, ticket_id: int):
        leido = container.obtener_ticket().ejecutar(ObtenerTicketInputDTO(self.hogar.pk, self.actor, ticket_id))
        if leido is None:
            raise consultas.no_encontrado(TicketModel)  # el mismo 404 que get_object()
        return leido

    def _respuesta(self, ticket_id: int, codigo=status.HTTP_200_OK):
        ticket = presentar(self._leer(ticket_id))  # la response, del lado de lectura (módulo 87)
        return Response(TicketSerializer(ticket, context=self.get_serializer_context()).data, status=codigo)

    def list(self, request, *args, **kwargs):
        filtro = consultas.filtros(
            consultas.filterset_de_la_view(self, TicketModel), request, TicketModel
        ).form.cleaned_data
        entrada = ListarTicketsInputDTO(
            self.hogar.pk,
            self.actor,
            estado=filtro.get("estado") or None,
            cuenta_id=filtro["cuenta"].pk if filtro.get("cuenta") else None,
            busqueda=consultas.busqueda(request),
            orden=consultas.orden(self, request, TicketModel),
            paginacion=self.paginator.paginacion(request),
        )
        pagina = container.listar_tickets().ejecutar(entrada)
        datos = self.get_serializer([presentar(t) for t in pagina.results], many=True).data
        return self.paginator.respuesta(request, pagina, datos)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(presentar(self._leer(consultas.id_de_la_url(self)))).data)

    @extend_schema(responses={202: TicketSerializer})
    def create(self, request, *args, **kwargs):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        datos = entrada.validated_data
        subida = SubirTicketInputDTO(
            hogar_id=self.hogar.pk,
            actor=self.actor,
            cuenta_id=datos["cuenta"].pk,
            contenido=datos["archivo"],
            nombre_original=datos["archivo"].name,
            tipo_archivo=datos["tipo"],
            huella_archivo=datos["huella_archivo"],
        )
        return self._respuesta(container.subir_ticket().ejecutar(subida).id, status.HTTP_202_ACCEPTED)

    def perform_destroy(self, instance):
        container.borrar_ticket().ejecutar(BorrarTicketInputDTO(self.hogar.pk, self.actor, instance.pk))

    @extend_schema(request=ConfirmarTicketSerializer, responses={200: TicketSerializer})
    @action(detail=True, methods=["post"])
    def confirmar(self, request, *args, **kwargs):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        ticket_id = self._leer(consultas.id_de_la_url(self)).id
        confirmacion = ConfirmarTicketInputDTO(
            hogar_id=self.hogar.pk, actor=self.actor, ticket_id=ticket_id, **entrada.a_dominio()
        )
        return self._respuesta(container.confirmar_ticket().ejecutar(confirmacion).id)

    @extend_schema(request=ReprocesarTicketSerializer, responses={202: TicketSerializer})
    @action(detail=True, methods=["post"])
    def reprocesar(self, request, *args, **kwargs):
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        ticket_id = self._leer(consultas.id_de_la_url(self)).id
        reproceso = ReprocesarTicketInputDTO(self.hogar.pk, self.actor, ticket_id, **entrada.validated_data)
        return self._respuesta(container.reprocesar_ticket().ejecutar(reproceso).id, status.HTTP_202_ACCEPTED)

    @extend_schema(responses={200: UrlArchivoSerializer})
    @action(detail=True, methods=["get"])
    def archivo(self, request, *args, **kwargs):
        """URL temporal del archivo (firmada en S3/R2: caduca sola). Un <img> no puede enviar el JWT."""
        nombre = self._leer(consultas.id_de_la_url(self)).archivo
        return Response({"url": request.build_absolute_uri(default_storage.url(nombre))})
