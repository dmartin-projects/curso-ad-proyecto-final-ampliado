# usuarios/infrastructure/providers/proveedores_configurados.py — IProveedores: los proveedores configurados (módulo 91)
#
# Un proveedor existe para Gastos si tiene client_id en settings.SOCIAL_LOGIN. La vuelta (redirect URI) es fija por
# entorno: el dominio de la app (FRONTEND_URL; en producción, Vercel reenvía /api/* a Django), nunca la del Host de la
# petición. Es la que se registra, exacta, en la consola de cada proveedor.
from django.conf import settings

from usuarios.application.ports.i_proveedores import IProveedores
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.proveedor_no_disponible_exception import ProveedorNoDisponibleException
from usuarios.infrastructure.providers.apple import Apple
from usuarios.infrastructure.providers.github import GitHub
from usuarios.infrastructure.providers.google import Google

CLASES = {Proveedor.GOOGLE: Google, Proveedor.GITHUB: GitHub, Proveedor.APPLE: Apple}


def vuelta(proveedor: Proveedor) -> str:
    return f"{settings.FRONTEND_URL}/api/v1/auth/social/{proveedor}/vuelta/"


class ProveedoresConfigurados(IProveedores):
    def disponibles(self):
        return [p for p in CLASES if settings.SOCIAL_LOGIN.get(p, {}).get("client_id")]

    def de(self, proveedor):
        if proveedor not in self.disponibles():
            raise ProveedorNoDisponibleException()
        return CLASES[proveedor](**settings.SOCIAL_LOGIN[proveedor], vuelta=vuelta(proveedor))
