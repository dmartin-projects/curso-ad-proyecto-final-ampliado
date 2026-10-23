# usuarios/infrastructure/database/services/sesiones_orm.py — ISesiones con el ORM (módulos 35 y 92)
#
# Una sesión de la SPA es una cadena de refresh tokens (cada uso rota el anterior); el `sid` la nombra de principio a
# fin (va dentro de cada refresh y de cada access) y la fila recuerda cuál es el refresh vigente (`refresh_jti`). Con
# eso, la fila es la que decide: /auth/refresh/ solo renueva una sesión abierta, sin caducar y con su refresh vigente
# (RenovarSesionUseCase). Por eso aquí no hace falta la lista negra de simplejwt, que guardaba cada refresh token entero en
# la base de datos: de cada uno basta su jti, que no sirve para nada sin la firma.
# Cerrar una sesión tiene dos efectos: la fila queda cerrada (su refresh ya no renueva) y su sid queda en la caché
# durante lo que dura un access (JWTConSesion rechaza ya los access de 10 minutos que tenga).
import hashlib
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from usuarios.application.ports.i_sesiones import ISesiones
from usuarios.domain.enums.canal import Canal
from usuarios.domain.enums.estado_renovacion import EstadoRenovacion
from usuarios.domain.enums.factor import Factor
from usuarios.domain.exceptions.sesion_no_encontrada_exception import SesionNoEncontradaException
from usuarios.domain.services.dispositivos import describir_dispositivo, ip_aproximada
from usuarios.domain.services.renovacion import clasificar_refresh
from usuarios.domain.vo.autenticacion import Autenticacion
from usuarios.domain.vo.renovacion import Renovacion
from usuarios.infrastructure.database.models.sesion_model import Sesion as SesionModel


def clave_cerrada(sid: str) -> str:
    return f"sesion:cerrada:{sid}"


def huella(dispositivo: str) -> str:
    return hashlib.sha256(dispositivo.encode()).hexdigest()  # la cookie no se guarda: quien lea la BD no la tiene


def _uuid(sid: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(sid))
    except ValueError:
        return None


def vida(canal: str):
    """Lo que dura una sesión sin usarse: la de la SPA, lo que su refresh (cada renovación vuelve a empezar); la del
    authorization server, lo que su sesión de Django."""
    if canal == Canal.SPA:
        return settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
    return timedelta(seconds=settings.SESSION_COOKIE_AGE)


def vigentes():
    """Las sesiones abiertas: ni cerradas ni caducadas (una sesión abandonada no se queda «abierta» para siempre)."""
    return SesionModel.objects.filter(cerrada__isnull=True, caduca__gt=timezone.now())


class SesionesORM(ISesiones):
    def cerrar_todas(self, usuario_id):
        """Al cambiar o recuperar la contraseña: todas sus sesiones, cerradas."""
        self._cerrar(vigentes().filter(usuario_id=usuario_id))

    def abrir(self, *, usuario_id, canal, autenticacion, contexto):
        ahora = timezone.now()
        sesion = SesionModel.objects.create(
            sid=uuid.uuid4(), usuario_id=usuario_id, canal=canal, factores=sorted(autenticacion.factores),
            passkey_sincronizada=autenticacion.passkey_sincronizada, autenticada=autenticacion.momento,
            creada=ahora, ultimo_uso=ahora, caduca=ahora + vida(canal), dispositivo=huella(contexto.dispositivo),
            descripcion=describir_dispositivo(contexto.user_agent), ip=ip_aproximada(contexto.ip),
        )  # fmt: skip
        return str(sesion.sid)

    def refresh_emitido(self, sid, jti):
        SesionModel.objects.filter(sid=_uuid(sid)).update(refresh_jti=jti)

    def autenticacion(self, sid):
        fila = vigentes().filter(sid=_uuid(sid)).first() if _uuid(sid) else None
        if fila is None:
            return None
        return Autenticacion(frozenset(Factor(f) for f in fila.factores), fila.autenticada, fila.passkey_sincronizada)

    def reautenticada(self, sid, autenticacion):
        SesionModel.objects.filter(sid=_uuid(sid)).update(
            factores=sorted(autenticacion.factores), autenticada=autenticacion.momento,
            passkey_sincronizada=autenticacion.passkey_sincronizada,
        )  # fmt: skip

    def rotar(self, sid, *, presentado, nuevo, contexto):
        if _uuid(sid) is None or not presentado:
            return Renovacion(EstadoRenovacion.CERRADA)
        ahora = timezone.now()
        abiertas = vigentes().filter(sid=_uuid(sid))
        cambios = {"refresh_jti": nuevo, "refresh_jti_anterior": presentado, "ultimo_uso": ahora,
                   "caduca": ahora + vida(Canal.SPA)}  # fmt: skip
        if contexto.ip:
            cambios["ip"] = ip_aproximada(contexto.ip)
        # Un UPDATE condicionado al refresh vigente: de dos peticiones con el mismo refresh, solo una lo rota
        if abiertas.filter(refresh_jti=presentado).update(**cambios) == 1:
            return Renovacion(EstadoRenovacion.ROTADA)
        fila = abiertas.first()
        if fila is None:
            return Renovacion(EstadoRenovacion.CERRADA)
        estado = clasificar_refresh(
            presentado=presentado, anterior=fila.refresh_jti_anterior, desde_la_rotacion=ahora - fila.ultimo_uso
        )
        return Renovacion(estado, fila.usuario_id, fila.descripcion)

    def cerrar(self, usuario_id, sid):
        sesiones = vigentes().filter(usuario_id=usuario_id, sid=_uuid(sid))
        if _uuid(sid) is None or not sesiones.exists():
            raise SesionNoEncontradaException()
        self._cerrar(sesiones)

    def cerrar_las_demas(self, usuario_id, sid):
        return self._cerrar(vigentes().filter(usuario_id=usuario_id).exclude(sid=_uuid(sid)))

    def dispositivo_conocido(self, usuario_id, dispositivo):
        return SesionModel.objects.filter(usuario_id=usuario_id, dispositivo=huella(dispositivo)).exists()

    def cuantas(self, usuario_id):
        return SesionModel.objects.filter(usuario_id=usuario_id).count()

    def _cerrar(self, sesiones) -> int:
        vida_del_access = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
        sids = list(sesiones.values_list("sid", flat=True))
        for sid in sids:
            cache.set(clave_cerrada(str(sid)), True, timeout=vida_del_access)
        return sesiones.update(cerrada=timezone.now()) if sids else 0
