# usuarios/tests/fakes/passkey_command_repository_fake.py — IPasskeyCommandRepository en memoria (módulo 92)
import dataclasses

from usuarios.domain.exceptions.passkey_no_encontrada_exception import PasskeyNoEncontradaException
from usuarios.domain.repositories.i_passkey_command_repository import IPasskeyCommandRepository


class PasskeyCommandRepositoryFake(IPasskeyCommandRepository):
    def __init__(self):
        self.filas: dict[int, object] = {}
        self.manijas: dict[int, bytes] = {}

    def de_usuario(self, usuario_id):
        return [dataclasses.replace(p) for p in self.filas.values() if p.usuario_id == usuario_id]

    def por_credencial(self, credencial_id):
        return next((dataclasses.replace(p) for p in self.filas.values() if p.credencial_id == credencial_id), None)

    def guardar(self, passkey):
        if passkey.id is None:
            passkey.id = len(self.filas) + 1
        self.filas[passkey.id] = dataclasses.replace(passkey)

    def borrar(self, usuario_id, passkey_id):
        p = self.filas.get(passkey_id)
        if p is None or p.usuario_id != usuario_id:
            raise PasskeyNoEncontradaException()
        del self.filas[passkey_id]
        return p.nombre

    def manija(self, usuario_id):
        return self.manijas.setdefault(usuario_id, f"manija-{usuario_id}".encode())

    def usuario_de_manija(self, manija):
        return next((u for u, m in self.manijas.items() if m == manija), None)
