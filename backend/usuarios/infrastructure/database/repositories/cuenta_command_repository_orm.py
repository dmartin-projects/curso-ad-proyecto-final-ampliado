# usuarios/infrastructure/database/repositories/cuenta_command_repository_orm.py — ICuentaCommandRepository con el modelo de usuario de Django (módulo 88)
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.exceptions.email_ya_registrado_exception import EmailYaRegistradoException
from usuarios.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


class CuentaCommandRepositoryORM(ICuentaCommandRepository):
    def __init__(self):
        self.Usuario = get_user_model()

    def por_email(self, email):
        return self.Usuario.objects.filter(email__iexact=email).values_list("pk", flat=True).first()

    def estado(self, usuario_id):
        usuario = self.Usuario.objects.get(pk=usuario_id)
        return EstadoCuenta.de(activa=usuario.is_active, con_contrasena=usuario.has_usable_password())

    def crear_pendiente(self, *, email, nombre, apellidos):
        try:
            with transaction.atomic():
                # password=None → set_unusable_password(): nadie entra con contraseña hasta completar el registro
                return self.Usuario.objects.create_user(
                    email=email, nombre=nombre, apellidos=apellidos, password=None, is_active=False
                ).pk
        except IntegrityError as e:  # dos registros a la vez con el mismo email: la constraint unique de email
            raise EmailYaRegistradoException() from e

    def completar_registro(self, usuario_id, password):
        usuario = self.Usuario.objects.get(pk=usuario_id)
        usuario.set_password(password)  # ⚠️ nunca usuario.password = password
        usuario.is_active = True
        usuario.save(update_fields=["password", "is_active"])  # un solo UPDATE: las dos cosas o ninguna

    def comprobar_contrasena(self, usuario_id, password):
        return self.Usuario.objects.get(pk=usuario_id).check_password(password)

    def cambiar_contrasena(self, usuario_id, password):
        usuario = self.Usuario.objects.get(pk=usuario_id)
        usuario.set_password(password)  # ⚠️ nunca usuario.password = password
        usuario.save(update_fields=["password"])
