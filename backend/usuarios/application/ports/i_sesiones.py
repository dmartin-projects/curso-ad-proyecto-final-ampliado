# usuarios/application/ports/i_sesiones.py — las sesiones de una cuenta (módulos 88 y 92)
from abc import ABC, abstractmethod

from usuarios.domain.enums.canal import Canal
from usuarios.domain.vo.autenticacion import Autenticacion
from usuarios.domain.vo.contexto import Contexto
from usuarios.domain.vo.renovacion import Renovacion


class ISesiones(ABC):
    @abstractmethod
    def cerrar_todas(self, usuario_id: int) -> None:
        """Cierra todas sus sesiones: sus refresh tokens dejan de renovar y sus access, de valer."""

    # Módulo 92: cada sesión, con nombre (sid), desde dónde, cuándo y con qué factores
    @abstractmethod
    def abrir(self, *, usuario_id: int, canal: Canal, autenticacion: Autenticacion, contexto: Contexto) -> str:
        """Devuelve el sid. Recuerda el dispositivo (la cookie, con hash) para reconocerlo la próxima vez. Caduca
        como su credencial: la de la SPA, como su refresh; la del authorization server, como su sesión de Django."""

    @abstractmethod
    def refresh_emitido(self, sid: str, jti: str) -> None:
        """El primer refresh de la sesión (la SPA): el vigente."""

    @abstractmethod
    def autenticacion(self, sid: str) -> Autenticacion | None:
        """La de una sesión abierta; None si está cerrada, ha caducado o no existe."""

    @abstractmethod
    def reautenticada(self, sid: str, autenticacion: Autenticacion) -> None: ...

    @abstractmethod
    def rotar(self, sid: str, *, presentado: str, nuevo: str, contexto: Contexto) -> Renovacion:
        """Si `presentado` es el refresh vigente de una sesión abierta, `nuevo` pasa a serlo (de una vez: de dos
        peticiones con el mismo, solo una rota), con el último uso y la caducidad renovados. Si no, por qué no."""

    @abstractmethod
    def cerrar(self, usuario_id: int, sid: str) -> None:
        """La sesión de ESE usuario (SesionNoEncontradaException si no es suya o ya está cerrada): su refresh ya no la
        renueva y su access se rechaza desde ya."""

    @abstractmethod
    def cerrar_las_demas(self, usuario_id: int, sid: str) -> int: ...

    @abstractmethod
    def dispositivo_conocido(self, usuario_id: int, dispositivo: str) -> bool: ...

    @abstractmethod
    def cuantas(self, usuario_id: int) -> int:
        """Las que ha abierto alguna vez (abiertas o cerradas)."""
        ...
