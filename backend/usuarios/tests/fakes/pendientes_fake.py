# usuarios/tests/fakes/pendientes_fake.py — IPendientes en memoria (módulo 92)
import dataclasses

from usuarios.application.ports.i_pendientes import IPendientes


class PendientesFake(IPendientes):
    def __init__(self):
        self.guardados = {}

    def guardar(self, pendiente):
        clave = f"pendiente-{len(self.guardados) + 1}"
        self.guardados[clave] = pendiente
        return clave

    def leer(self, clave):
        return self.guardados.get(clave)

    def intento(self, clave):
        if (p := self.guardados.get(clave)) is None:
            return False
        if p.agotado:
            del self.guardados[clave]
            return False
        self.guardados[clave] = dataclasses.replace(p, intentos=p.intentos + 1)
        return True

    def consumir(self, clave):
        return self.guardados.pop(clave, None)
