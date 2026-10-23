# usuarios/tests/fakes/codigos_de_recuperacion_fake.py — ICodigosDeRecuperacion en memoria (módulo 92)
from usuarios.application.ports.i_codigos_de_recuperacion import ICodigosDeRecuperacion


class CodigosDeRecuperacionFake(ICodigosDeRecuperacion):
    def __init__(self):
        self.vigentes: dict[int, set[str]] = {}

    def generar(self, usuario_id):
        self.vigentes[usuario_id] = {f"CODIGO-{usuario_id}-{i}" for i in range(10)}
        return sorted(self.vigentes[usuario_id])

    def usar(self, usuario_id, codigo):
        if codigo in self.vigentes.get(usuario_id, set()):
            self.vigentes[usuario_id].discard(codigo)
            return True
        return False

    def quedan(self, usuario_id):
        return len(self.vigentes.get(usuario_id, set()))

    def borrar(self, usuario_id):
        self.vigentes.pop(usuario_id, None)
