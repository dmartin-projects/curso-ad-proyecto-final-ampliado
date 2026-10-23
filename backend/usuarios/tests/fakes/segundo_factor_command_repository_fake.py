# usuarios/tests/fakes/segundo_factor_command_repository_fake.py — ISegundoFactorCommandRepository en memoria
# (módulo 92)
import dataclasses

from usuarios.domain.bo.segundo_factor import SegundoFactor
from usuarios.domain.repositories.i_segundo_factor_command_repository import ISegundoFactorCommandRepository


class SegundoFactorCommandRepositoryFake(ISegundoFactorCommandRepository):
    def __init__(self):
        self.guardados: dict[int, SegundoFactor] = {}
        self.bloqueos: list[int] = []

    def de(self, usuario_id, *, bloquear=False):
        if bloquear:
            self.bloqueos.append(usuario_id)
        return dataclasses.replace(self.guardados.get(usuario_id) or SegundoFactor(usuario_id))  # una copia: como la BD

    def guardar(self, segundo):
        self.guardados[segundo.usuario_id] = dataclasses.replace(segundo)
