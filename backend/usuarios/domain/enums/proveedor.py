# usuarios/domain/enums/proveedor.py — con quién se puede entrar además de la contraseña (módulo 91)
#
# Se puede entrar en Gastos con la contraseña o con una cuenta de otro proveedor (Google, GitHub, Apple). El protocolo
# (OIDC, OAuth 2.0) es de los adapters; lo que es de Gastos está en el dominio: a qué cuenta lleva cada identidad
# externa, cuándo se crea una cuenta nueva, por qué NO se vincula nada solo porque coincida el email
# (services/social_login.py), adónde se puede volver después (services/destino_seguro.py) y que nadie se quede sin
# forma de entrar (vo/metodos_de_acceso.py).
from enum import StrEnum

from usuarios.domain.exceptions.proveedor_no_disponible_exception import ProveedorNoDisponibleException


class Proveedor(StrEnum):
    GOOGLE = "google"
    GITHUB = "github"
    APPLE = "apple"

    @classmethod
    def de(cls, texto: str) -> "Proveedor":
        """El de una URL (/social/<proveedor>/…): uno que no existe es un 404, no un 500."""
        try:
            return cls(texto)
        except ValueError:
            raise ProveedorNoDisponibleException() from None

    @property
    def nombre(self) -> str:
        return {"google": "Google", "github": "GitHub", "apple": "Apple"}[self.value]
