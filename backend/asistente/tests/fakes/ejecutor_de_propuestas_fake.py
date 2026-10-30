# asistente/tests/fakes/ejecutor_de_propuestas_fake.py — IEjecutorDePropuestas que apunta lo ejecutado (módulo 97)
from asistente.application.ports.i_ejecutor_de_propuestas import IEjecutorDePropuestas
from core.domain.enums.rol import Rol


class EjecutorDePropuestasFake(IEjecutorDePropuestas):
    """Como el de verdad, exige el rol de la app dueña (miembro) al Actor que confirma."""

    def __init__(self, fallo: Exception | None = None):
        self.ejecutadas: list[tuple] = []
        self.fallo = fallo

    def ejecutar(self, propuesta, actor):
        actor.exigir(Rol.MIEMBRO)
        if self.fallo:
            raise self.fallo
        self.ejecutadas.append((propuesta.id, actor))
        return {"movimiento_id": 100 + len(self.ejecutadas)}
