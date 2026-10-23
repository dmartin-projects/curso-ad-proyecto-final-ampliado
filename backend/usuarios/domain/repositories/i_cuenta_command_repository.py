# usuarios/domain/repositories/i_cuenta_command_repository.py — lo que las cuentas necesitan de Django auth (módulos 88 y 91)
from abc import ABC, abstractmethod

from usuarios.domain.enums.estado_cuenta import EstadoCuenta


class ICuentaCommandRepository(ABC):
    """Las cuentas de usuario, sobre el modelo de Django auth (AbstractBaseUser): el hash lo pone Django."""

    @abstractmethod
    def por_email(self, email: str) -> int | None:
        """La cuenta con ese email (sin distinguir mayúsculas), esté como esté."""

    @abstractmethod
    def estado(self, usuario_id: int) -> EstadoCuenta: ...

    @abstractmethod
    def crear_pendiente(self, *, email: str, nombre: str, apellidos: str) -> int:
        """Una cuenta INACTIVA y SIN contraseña: nadie entra hasta completar el registro. Email repetido a la vez:
        EmailYaRegistradoException."""

    @abstractmethod
    def completar_registro(self, usuario_id: int, password: str) -> None:
        """Pone la contraseña (con hash) y activa la cuenta, en una sola escritura. El hash nuevo invalida el enlace."""

    @abstractmethod
    def comprobar_contrasena(self, usuario_id: int, password: str) -> bool: ...

    @abstractmethod
    def cambiar_contrasena(self, usuario_id: int, password: str) -> None:
        """Con hash. Cambiarla invalida los enlaces de recuperación ya enviados (el token depende del hash)."""

    # Módulo 91: las cuentas que llegan de un proveedor
    @abstractmethod
    def crear_verificada(self, *, email: str, nombre: str, apellidos: str) -> int:
        """Una cuenta ACTIVA (el proveedor ha verificado el email) y sin contraseña. Email repetido a la vez:
        EmailYaRegistradoException."""

    @abstractmethod
    def activa(self, usuario_id: int) -> bool: ...

    @abstractmethod
    def tiene_contrasena(self, usuario_id: int) -> bool: ...

    @abstractmethod
    def bloquear(self, usuario_id: int) -> None:
        """Hasta el final de la transacción, nadie más cambia las formas de entrar de esta cuenta."""
