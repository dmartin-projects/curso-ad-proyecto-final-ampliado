# usuarios/tests/fakes/retos_fake.py — IRetos en memoria (módulo 92)
from usuarios.application.ports.i_retos import IRetos


class RetosFake(IRetos):
    def __init__(self):
        self.guardados: dict[str, bytes] = {}

    def guardar(self, ambito, challenge):
        self.guardados[ambito] = challenge

    def consumir(self, ambito):
        return self.guardados.pop(ambito, None)
