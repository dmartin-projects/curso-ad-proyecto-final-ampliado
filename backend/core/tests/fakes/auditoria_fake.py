# core/tests/fakes/auditoria_fake.py — IAuditoria en memoria (módulos 87 y 88)
from core.application.ports.i_auditoria import IAuditoria
from core.domain.enums.accion import Accion
from core.domain.services.diferencias import diferencias


class AuditoriaFake(IAuditoria):
    def __init__(self):
        self.registros: list[tuple] = []
        self.fallar = False

    def registrar(self, accion: Accion, objeto, usuario_id, antes=None):
        if self.fallar:
            raise RuntimeError("la auditoría se ha caído")
        cambios = diferencias(antes.datos_auditables(), objeto.datos_auditables()) if antes else {}
        self.registros.append((accion, objeto.tipo, objeto.id, usuario_id, cambios))

    def registrar_varios(self, accion: Accion, objetos, usuario_id, antes=None):
        for objeto, previo in zip(objetos, antes or [None] * len(objetos), strict=True):
            self.registrar(accion, objeto, usuario_id, previo)
