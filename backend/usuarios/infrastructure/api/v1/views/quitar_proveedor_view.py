# usuarios/infrastructure/api/v1/views/quitar_proveedor_view.py — desvincular un proveedor (módulo 91)
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.application.desvincular_use_case.dtos.desvincular_input_dto import DesvincularInputDTO
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.infrastructure import container


class QuitarProveedorView(APIView):
    def delete(self, request, proveedor, **kwargs):
        container.desvincular().ejecutar(DesvincularInputDTO(request.user.pk, Proveedor.de(proveedor)))
        return Response(status=204)
