# usuarios/infrastructure/cache/transacciones_en_cache.py — ITransacciones en la caché de Django (Redis) (módulo 91)
#
# Lo que hay que recordar entre la ida al proveedor y la vuelta (state, nonce, code_verifier…) se queda en el
# SERVIDOR, con caducidad; el navegador solo lleva una clave aleatoria en una cookie HttpOnly. No va en la sesión de
# Django: su cookie solo viaja a /api/oauth/ (módulo 90), y la SPA no usa sesiones.
import dataclasses
import hashlib
import secrets

from django.conf import settings
from django.core.cache import cache

from usuarios.application.ports.i_transacciones import ITransacciones
from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.vo.transaccion_social import TransaccionSocial


def _clave_cache(clave: str) -> str:
    # El hash, no la clave: quien lea Redis (un volcado, un MONITOR) no puede ponerse esa cookie
    return "social:transaccion:" + hashlib.sha256(clave.encode()).hexdigest()


class TransaccionesEnCache(ITransacciones):
    def guardar(self, transaccion):
        clave = secrets.token_urlsafe(32)
        cache.set(_clave_cache(clave), dataclasses.asdict(transaccion), timeout=settings.SOCIAL_LOGIN_SEGUNDOS)
        return clave

    def consumir(self, clave):
        datos = cache.get(_clave_cache(clave))
        # delete() dice si la clave existía: de dos vueltas a la vez con la misma cookie, solo una la consume
        if datos is None or not cache.delete(_clave_cache(clave)):
            return None
        return TransaccionSocial(
            **datos | {"proveedor": Proveedor(datos["proveedor"]), "proposito": Proposito(datos["proposito"])}
        )
