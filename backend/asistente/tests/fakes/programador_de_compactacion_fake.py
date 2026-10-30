# asistente/tests/fakes/programador_de_compactacion_fake.py (módulo 99)
from asistente.application.ports.i_programador_de_compactacion import IProgramadorDeCompactacion


class ProgramadorDeCompactacionFake(IProgramadorDeCompactacion):
    """Apunta lo que se programa; el test decide si lo ejecuta (con el use case de compactar)."""

    def __init__(self):
        self.programadas: list[tuple[int, int, int]] = []

    def programar(self, usuario_id, hogar_id, conversacion_id):
        self.programadas.append((usuario_id, hogar_id, conversacion_id))
