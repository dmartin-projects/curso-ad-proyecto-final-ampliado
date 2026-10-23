# usuarios/infrastructure/cache/retos_en_cache.py — IRetos en la caché de Django (Redis) (módulo 92)
import hashlib

from django.core.cache import cache

from usuarios.application.ports.i_retos import IRetos


class RetosEnCache(IRetos):
    def guardar(self, ambito, challenge):
        cache.set("webauthn:reto:" + hashlib.sha256(ambito.encode()).hexdigest(), challenge, timeout=300)

    def consumir(self, ambito):
        clave = "webauthn:reto:" + hashlib.sha256(ambito.encode()).hexdigest()
        challenge = cache.get(clave)
        return challenge if challenge is not None and cache.delete(clave) else None
