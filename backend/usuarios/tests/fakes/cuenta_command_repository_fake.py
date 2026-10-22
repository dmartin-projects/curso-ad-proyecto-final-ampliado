# usuarios/tests/fakes/cuenta_command_repository_fake.py — ICuentaCommandRepository en memoria (módulos 35 y 88)
from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.exceptions.email_ya_registrado_exception import EmailYaRegistradoException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


class CuentaCommandRepositoryFake(ICuentaCommandRepository):
    def __init__(self):
        self.usuarios: dict[int, dict] = {}

    def por_email(self, email):
        return next((pk for pk, u in self.usuarios.items() if u["email"].lower() == email.lower()), None)

    def estado(self, usuario_id):
        u = self.usuarios[usuario_id]
        return EstadoCuenta.de(activa=u["activo"], con_contrasena=u["password"] is not None)

    def crear_pendiente(self, *, email, nombre, apellidos):
        if self.por_email(email) is not None:
            raise EmailYaRegistradoException()
        pk = len(self.usuarios) + 1
        self.usuarios[pk] = {"email": email, "nombre": nombre, "password": None, "activo": False}
        return pk

    def completar_registro(self, usuario_id, password):
        self.usuarios[usuario_id] |= {"password": password, "activo": True}

    def comprobar_contrasena(self, usuario_id, password):
        return self.usuarios[usuario_id]["password"] == password

    def cambiar_contrasena(self, usuario_id, password):
        self.usuarios[usuario_id]["password"] = password
