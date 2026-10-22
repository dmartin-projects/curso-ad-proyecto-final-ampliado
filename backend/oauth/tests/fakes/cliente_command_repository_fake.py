# oauth/tests/fakes/cliente_command_repository_fake.py — IClienteCommandRepository en memoria (módulo 90)
import secrets

from oauth.domain.exceptions.cliente_ya_existe_exception import ClienteYaExisteException
from oauth.domain.repositories.i_cliente_command_repository import IClienteCommandRepository
from oauth.domain.vo.credenciales import Credenciales


class ClienteCommandRepositoryFake(IClienteCommandRepository):
    def __init__(self):
        self.clientes: dict[str, object] = {}

    def existe(self, client_id):
        return client_id in self.clientes

    def crear(self, cliente):
        client_id = cliente.client_id or secrets.token_urlsafe(30)
        if client_id in self.clientes:
            raise ClienteYaExisteException()
        self.clientes[client_id] = cliente
        return Credenciales(client_id, secrets.token_urlsafe(48) if cliente.tipo.confidencial else None)
