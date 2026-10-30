# asistente/tests/fakes/avisos_de_progreso_fake.py — IAvisosDeProgreso que apunta (módulo 105)
from asistente.application.ports.i_avisos_de_progreso import IAvisosDeProgreso


class AvisosDeProgresoFake(IAvisosDeProgreso):
    def __init__(self):
        self.avisos: list[tuple[int, int, str, dict]] = []

    def avisar(self, usuario_id, hogar_id, tarea, datos):
        self.avisos.append((usuario_id, hogar_id, tarea, datos))

    @property
    def pasos(self) -> list[str]:
        return [d["paso"] for *_, d in self.avisos]
