# usuarios/domain/bo/passkey.py — una passkey de una cuenta (módulo 92)
#
# Una passkey es un par de claves que crea el autenticador (el del móvil, el portátil, una llave USB o el gestor de
# contraseñas) para ESTE sitio (el rp_id): Gastos guarda la clave pública; la privada no sale del autenticador (o de
# su sincronización cifrada). Al entrar, el autenticador firma un reto de un solo uso: no hay nada que robar en Gastos
# ni nada que teclear en una web falsa (la firma incluye el origen).
from dataclasses import dataclass

from usuarios.domain.exceptions.nombre_de_passkey_no_valido_exception import NombreDePasskeyNoValidoException


@dataclass(eq=False)
class Passkey:
    usuario_id: int
    credencial_id: bytes  # lo elige el autenticador; único en el mundo
    clave_publica: bytes  # COSE (RFC 9052): la que comprueba las firmas
    contador: int  # signCount: si un autenticador lo lleva, solo puede crecer (uno que retrocede, ¿un clon?)
    nombre: str
    sincronizada: bool = False  # backup state (BS): vive en iCloud, Google Password Manager, 1Password…
    transportes: tuple[str, ...] = ()  # internal, hybrid, usb…: el navegador sabe por dónde buscarla
    id: int | None = None

    def __post_init__(self):
        self.nombre = (self.nombre or "").strip()
        if not 1 <= len(self.nombre) <= 60:
            raise NombreDePasskeyNoValidoException()
