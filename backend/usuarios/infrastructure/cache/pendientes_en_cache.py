# usuarios/infrastructure/cache/pendientes_en_cache.py — IPendientes en la caché de Django (Redis) (módulo 92)
import dataclasses
import hashlib
import secrets
import time

from django.conf import settings
from django.core.cache import cache

from usuarios.application.ports.i_pendientes import IPendientes
from usuarios.domain.enums.factor import Factor
from usuarios.domain.vo.login_pendiente import LoginPendiente


def _clave_pendiente(clave: str) -> str:
    return "mfa:pendiente:" + hashlib.sha256(clave.encode()).hexdigest()


class PendientesEnCache(IPendientes):
    """El login a medias. Como la transacción social: el navegador lleva una clave aleatoria (cookie HttpOnly) y aquí
    se guarda su hash. No es una sesión: con ella solo se puede intentar el segundo factor, unas pocas veces. (El
    límite de verdad es el de la cuenta, en la base de datos y con la fila bloqueada: SegundoFactor.fallos.)"""

    def guardar(self, pendiente):
        clave = secrets.token_urlsafe(32)
        self._poner(clave, pendiente, time.time() + settings.MFA_PENDIENTE_SEGUNDOS)
        return clave

    def leer(self, clave):
        datos = cache.get(_clave_pendiente(clave))
        return (
            LoginPendiente(**datos["pendiente"] | {"primero": Factor(datos["pendiente"]["primero"])}) if datos else None
        )

    def intento(self, clave):
        datos, pendiente = cache.get(_clave_pendiente(clave)), self.leer(clave)
        if pendiente is None:
            return False
        if pendiente.agotado:
            cache.delete(_clave_pendiente(clave))
            return False
        pendiente = dataclasses.replace(pendiente, intentos=pendiente.intentos + 1)
        self._poner(clave, pendiente, datos["caduca"])  # lo que le quedaba: un intento no alarga su vida
        return True

    def consumir(self, clave):
        pendiente = self.leer(clave)
        # delete() dice si existía: de dos peticiones a la vez, solo una abre la sesión
        return pendiente if pendiente is not None and cache.delete(_clave_pendiente(clave)) else None

    def _poner(self, clave, pendiente, caduca: float):
        datos = {"pendiente": dataclasses.asdict(pendiente), "caduca": caduca}
        cache.set(_clave_pendiente(clave), datos, timeout=max(1, int(caduca - time.time())))
