# oauth/application/registrar_cliente_use_case/registrar_cliente_use_case.py — registrar una aplicación cliente (módulo 90)
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from oauth.application.registrar_cliente_use_case.dtos.credenciales_output_dto import CredencialesOutputDTO
from oauth.application.registrar_cliente_use_case.dtos.registrar_cliente_input_dto import RegistrarClienteInputDTO
from oauth.application.registrar_cliente_use_case.i_registrar_cliente_use_case import IRegistrarClienteUseCase
from oauth.domain.bo.cliente_nuevo import ClienteNuevo
from oauth.domain.exceptions.cliente_ya_existe_exception import ClienteYaExisteException
from oauth.domain.repositories.i_cliente_command_repository import IClienteCommandRepository


class RegistrarClienteUseCase(IRegistrarClienteUseCase):
    """Solo desde el servidor (un comando): Gastos no tiene registro de clientes abierto (RFC 7591)."""

    def __init__(self, *, clientes: IClienteCommandRepository, uow: IUnidadDeTrabajo):
        self.clientes, self.uow = clientes, uow

    def ejecutar(self, entrada: RegistrarClienteInputDTO) -> CredencialesOutputDTO:
        cliente = ClienteNuevo(  # las reglas, antes de tocar nada
            nombre=entrada.nombre,
            tipo=entrada.tipo,
            scopes=frozenset(entrada.scopes),
            redirect_uris=tuple(entrada.redirect_uris),
            client_id=entrada.client_id,
        )
        with self.uow:
            if cliente.client_id is not None and self.clientes.existe(cliente.client_id):
                raise ClienteYaExisteException()
            return CredencialesOutputDTO.desde_vo(self.clientes.crear(cliente))
