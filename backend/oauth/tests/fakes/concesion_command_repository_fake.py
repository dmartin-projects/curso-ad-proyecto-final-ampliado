# oauth/tests/fakes/concesion_command_repository_fake.py — IConcesionCommandRepository en memoria (ejercicio 1 del módulo 90)
from oauth.domain.repositories.i_concesion_command_repository import IConcesionCommandRepository


class ConcesionCommandRepositoryFake(IConcesionCommandRepository):
    """{(usuario_id, client_id): sesiones vivas}."""

    def __init__(self):
        self.sesiones: dict[tuple[int, str], int] = {}

    def dar(self, usuario_id, client_id, sesiones=1):  # para preparar los tests
        self.sesiones[usuario_id, client_id] = self.sesiones.get((usuario_id, client_id), 0) + sesiones

    def tiene(self, usuario_id, client_id):
        return self.sesiones.get((usuario_id, client_id), 0) > 0

    def revocar(self, usuario_id, client_id):
        return self.sesiones.pop((usuario_id, client_id), 0)
