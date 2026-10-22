# finanzas/infrastructure/api/v1/views/cuenta_viewset.py — adapter de entrada HTTP (módulos 33-38 y 87)
from django.db.models import RestrictedError
from rest_framework.response import Response

from finanzas.application.listar_cuentas_use_case.dtos.listar_cuentas_input_dto import ListarCuentasInputDTO
from finanzas.application.obtener_cuenta_use_case.dtos.obtener_cuenta_input_dto import ObtenerCuentaInputDTO
from finanzas.domain.exceptions.cuenta_con_movimientos_exception import CuentaConMovimientosException
from finanzas.infrastructure import container
from finanzas.infrastructure.api.v1.presenters.cuenta_presenter import presentar
from finanzas.infrastructure.api.v1.serializers.cuenta_serializer import CuentaSerializer
from finanzas.infrastructure.api.v1.views import consultas
from finanzas.infrastructure.database.models.cuenta_model import Cuenta as CuentaModel
from hogares.api.base import DelHogarViewSet
from hogares.models import Membresia


# CRUD puro al escribir: sin reglas ni efectos, no hay use case de comando que escribir (módulo 87); crea y edita con
# el ORM. Lo único que no se permite, borrar una cuenta con movimientos, lo impide la base de datos (RESTRICT) y aquí
# se traduce. Leer (con el saldo), como cualquier otro recurso: use cases de consulta.
# (Un comentario y no un docstring: el docstring de una view es la descripción del endpoint en OpenAPI.)
class CuentaViewSet(DelHogarViewSet):
    modelo = CuentaModel
    serializer_class = CuentaSerializer
    pagination_class = None
    roles_por_metodo = {
        "GET": Membresia.Rol.LECTOR,
        "POST": Membresia.Rol.ADMIN,
        "PUT": Membresia.Rol.ADMIN,
        "PATCH": Membresia.Rol.ADMIN,
        "DELETE": Membresia.Rol.ADMIN,
    }

    def _leer(self, cuenta_id: int):
        leida = container.obtener_cuenta().ejecutar(ObtenerCuentaInputDTO(self.hogar.pk, self.actor, cuenta_id))
        if leida is None:
            raise consultas.no_encontrado(CuentaModel)
        return presentar(leida)

    def list(self, request, *args, **kwargs):
        entrada = ListarCuentasInputDTO(self.hogar.pk, self.actor, consultas.orden(self, request, CuentaModel))
        cuentas = container.listar_cuentas().ejecutar(entrada)
        return Response(self.get_serializer([presentar(c) for c in cuentas], many=True).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self._leer(consultas.id_de_la_url(self))).data)

    def perform_update(self, serializer):
        serializer.save()
        serializer.instance = self._leer(serializer.instance.pk)  # la response, con su saldo

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except RestrictedError:  # Movimiento.cuenta es RESTRICT: el historial no se borra con la cuenta
            raise CuentaConMovimientosException() from None
