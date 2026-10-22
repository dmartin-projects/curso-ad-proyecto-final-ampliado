# informes/infrastructure/api/v1/views/informe_viewset.py — adapter de entrada HTTP (módulos 78 y 88)
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.domain.vo.mes import Mes
from hogares.infrastructure.api.base.del_hogar_viewset import DelHogarViewSet
from informes.application.listar_informes_use_case.dtos.listar_informes_input_dto import ListarInformesInputDTO
from informes.application.obtener_informe_use_case.dtos.obtener_informe_input_dto import ObtenerInformeInputDTO
from informes.application.pedir_informe_use_case.dtos.pedir_informe_input_dto import PedirInformeInputDTO
from informes.infrastructure import container
from informes.infrastructure.api.v1.presenters.informe_presenter import presentar
from informes.infrastructure.api.v1.serializers.generar_informe_serializer import GenerarInformeSerializer
from informes.infrastructure.api.v1.serializers.informe_encolado_serializer import InformeEncoladoSerializer
from informes.infrastructure.api.v1.serializers.informe_serializer import InformeSerializer
from informes.infrastructure.database.models.informe_mensual_model import InformeMensual as InformeMensualModel


class InformeViewSet(DelHogarViewSet):
    """Informes mensuales en PDF: /informes/ · /informes/2026-10/ · /informes/2026-10/pdf/"""

    modelo = InformeMensualModel
    serializer_class = InformeSerializer
    http_method_names = ["get", "post", "head", "options"]
    pagination_class = None
    lookup_field = "mes"
    lookup_value_regex = r"\d{4}-\d{2}"

    def get_serializer_class(self):
        return GenerarInformeSerializer if self.action == "create" else InformeSerializer

    def _leer(self):
        """El informe del mes de la URL (AAAA-MM), o 404."""
        anio, mes = map(int, self.kwargs["mes"].split("-"))
        try:
            entrada = ObtenerInformeInputDTO(self.hogar.pk, self.actor, Mes(anio, mes))
        except ValueError as e:  # mes 13
            raise Http404 from e
        informe = container.obtener_informe().ejecutar(entrada)
        if informe is None:
            raise Http404
        return informe

    def list(self, request, *args, **kwargs):
        informes = container.listar_informes().ejecutar(ListarInformesInputDTO(self.hogar.pk, self.actor))
        return Response(self.get_serializer([presentar(i) for i in informes], many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(presentar(self._leer())).data)

    @extend_schema(request=GenerarInformeSerializer, responses={202: InformeEncoladoSerializer})
    def create(self, request, *args, **kwargs):
        """Genera (o regenera) un informe bajo demanda, en segundo plano."""
        entrada = self.get_serializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        pedido = PedirInformeInputDTO(self.hogar.pk, self.actor, **entrada.validated_data)
        mes = container.pedir_informe().ejecutar(pedido)
        return Response({"mes": str(mes), "estado": "generando"}, status=status.HTTP_202_ACCEPTED)

    @extend_schema(responses={(200, "application/pdf"): OpenApiResponse(description="El PDF")})
    @action(detail=True, methods=["get"])
    def pdf(self, request, *args, **kwargs):
        informe = self._leer()
        return FileResponse(  # se envía por trozos, sin cargar el PDF entero en memoria
            default_storage.open(informe.archivo, "rb"),
            as_attachment=True,  # Content-Disposition: attachment; filename="…" (lo lee Angular, módulo 51)
            filename=f"gastos-{self.hogar.nombre}-{informe.mes:%Y-%m}.pdf",
            content_type="application/pdf",
        )
