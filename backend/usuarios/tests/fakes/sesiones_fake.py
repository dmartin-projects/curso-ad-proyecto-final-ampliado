# usuarios/tests/fakes/sesiones_fake.py — ISesiones en memoria (módulos 35, 88 y 92)
import uuid
from datetime import UTC, datetime

from usuarios.application.ports.i_sesiones import ISesiones
from usuarios.domain.enums.estado_renovacion import EstadoRenovacion
from usuarios.domain.exceptions.sesion_no_encontrada_exception import SesionNoEncontradaException
from usuarios.domain.services.dispositivos import describir_dispositivo
from usuarios.domain.services.renovacion import clasificar_refresh
from usuarios.domain.vo.renovacion import Renovacion


class SesionesFake(ISesiones):
    """Módulo 92: cada sesión, un dict; cerradas, con `cerrada=True`. (La caducidad, con el ORM: test_mfa_api.py.)"""

    def __init__(self):
        self.cerradas: list[int] = []  # cerrar_todas (cambiar la contraseña)
        self.filas: dict[str, dict] = {}

    def cerrar_todas(self, usuario_id):
        self.cerradas.append(usuario_id)
        for f in self.filas.values():
            if f["usuario_id"] == usuario_id:
                f["cerrada"] = True

    def abrir(self, *, usuario_id, canal, autenticacion, contexto):
        sid = str(uuid.uuid4())
        self.filas[sid] = {"usuario_id": usuario_id, "canal": canal, "autenticacion": autenticacion,
                           "dispositivo": contexto.dispositivo, "cerrada": False, "jti": "", "anterior": "",
                           "rotada": datetime.now(UTC), "descripcion": describir_dispositivo(contexto.user_agent)}  # fmt: skip
        return sid

    def refresh_emitido(self, sid, jti):
        self.filas[sid]["jti"] = jti

    def autenticacion(self, sid):
        f = self.filas.get(sid)
        return f["autenticacion"] if f and not f["cerrada"] else None

    def reautenticada(self, sid, autenticacion):
        self.filas[sid]["autenticacion"] = autenticacion

    def rotar(self, sid, *, presentado, nuevo, contexto):
        f = self.filas.get(sid)
        if not f or f["cerrada"]:
            return Renovacion(EstadoRenovacion.CERRADA)
        if f["jti"] == presentado:
            f["jti"], f["anterior"], f["rotada"] = nuevo, presentado, datetime.now(UTC)
            return Renovacion(EstadoRenovacion.ROTADA)
        estado = clasificar_refresh(
            presentado=presentado, anterior=f["anterior"], desde_la_rotacion=datetime.now(UTC) - f["rotada"]
        )
        return Renovacion(estado, f["usuario_id"], f["descripcion"])

    def cerrar(self, usuario_id, sid):
        f = self.filas.get(sid)
        if not f or f["cerrada"] or f["usuario_id"] != usuario_id:
            raise SesionNoEncontradaException()
        f["cerrada"] = True

    def cerrar_las_demas(self, usuario_id, sid):
        otras = [f for s, f in self.filas.items() if s != sid and f["usuario_id"] == usuario_id and not f["cerrada"]]
        for f in otras:
            f["cerrada"] = True
        return len(otras)

    def dispositivo_conocido(self, usuario_id, dispositivo):
        return any(f["usuario_id"] == usuario_id and f["dispositivo"] == dispositivo for f in self.filas.values())

    def cuantas(self, usuario_id):
        return sum(f["usuario_id"] == usuario_id for f in self.filas.values())
