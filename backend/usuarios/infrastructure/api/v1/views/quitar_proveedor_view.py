# usuarios/infrastructure/api/v1/views/quitar_proveedor_view.py — desvincular un proveedor (módulos 91 y 92)
from rest_framework.response import Response

from usuarios.application.desvincular_use_case.dtos.desvincular_input_dto import DesvincularInputDTO
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.infrastructure import container
from usuarios.infrastructure.api.v1.views.con_step_up import ConStepUp


class QuitarProveedorView(ConStepUp):
    def delete(self, request, proveedor, **kwargs):
        container.desvincular().ejecutar(DesvincularInputDTO(request.user.pk, Proveedor.de(proveedor)))
        return Response(status=204)
