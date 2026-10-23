# usuarios/tests/fakes/transacciones_fake.py — ITransacciones en memoria (módulo 91)
from usuarios.application.ports.i_transacciones import ITransacciones


class TransaccionesFake(ITransacciones):
    def __init__(self):
        self.guardadas = {}

    def guardar(self, transaccion):
        clave = f"clave-{len(self.guardadas) + 1}"
        self.guardadas[clave] = transaccion
        return clave

    def consumir(self, clave):
        return self.guardadas.pop(clave, None)
