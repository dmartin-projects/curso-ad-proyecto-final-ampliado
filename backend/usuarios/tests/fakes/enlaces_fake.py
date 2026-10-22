# usuarios/tests/fakes/enlaces_fake.py — IEnlaces en memoria (módulos 35 y 88)
from usuarios.application.ports.i_enlaces import IEnlaces


class EnlacesFake(IEnlaces):
    def crear(self, usuario_id, ruta):
        return f"https://app/{ruta}?uid={usuario_id}&token=ok"

    def usuario_de(self, uid, token):
        return int(uid) if token == "ok" else None
