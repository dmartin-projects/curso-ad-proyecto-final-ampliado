# usuarios/tests/fakes/sesiones_fake.py — ISesiones en memoria (módulos 35 y 88)
from usuarios.application.ports.i_sesiones import ISesiones


class SesionesFake(ISesiones):
    def __init__(self):
        self.cerradas: list[int] = []

    def cerrar_todas(self, usuario_id):
        self.cerradas.append(usuario_id)
