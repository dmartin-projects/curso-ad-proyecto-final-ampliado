# asistente/infrastructure/database/repositories/conversacion_query_service_orm.py (módulo 97)
from django.db.models import Count, Q

from asistente.domain.read_models.carpeta_listada import CarpetaListada
from asistente.domain.read_models.conversacion_detalle import ConversacionDetalle
from asistente.domain.read_models.conversacion_listada import ConversacionListada
from asistente.domain.read_models.mensaje_visible import MensajeVisible
from asistente.domain.repositories.i_conversacion_query_service import IConversacionQueryService
from asistente.infrastructure.database.models.carpeta_model import Carpeta as CarpetaModel
from asistente.infrastructure.database.models.conversacion_model import Conversacion as ConversacionModel
from asistente.infrastructure.database.models.mensaje_model import Mensaje as MensajeModel
from asistente.infrastructure.database.models.propuesta_model import Propuesta as PropuestaModel

CAMPOS = ("id", "titulo", "carpeta_id", "actualizado")


def _listada(fila: dict) -> ConversacionListada:
    return ConversacionListada(fila["id"], fila["titulo"], fila["carpeta_id"], fila["actualizado"])


class ConversacionQueryServiceORM(IConversacionQueryService):
    def listar(self, usuario_id, hogar_id, carpeta_id=None, limite=50, busqueda=None):
        filas = ConversacionModel.objects.filter(usuario_id=usuario_id, hogar_id=hogar_id)
        if carpeta_id is not None:
            filas = filas.filter(carpeta_id=carpeta_id)
        if busqueda:  # ejercicio 2: unaccent (la extensión del módulo 73), como la búsqueda de movimientos
            en_mensajes = MensajeModel.objects.filter(visible=True, texto__unaccent__icontains=busqueda)
            filas = filas.filter(
                Q(titulo__unaccent__icontains=busqueda) | Q(pk__in=en_mensajes.values("conversacion_id"))
            )
        return tuple(_listada(f) for f in filas.order_by("-actualizado", "-id").values(*CAMPOS)[:limite])

    def detalle(self, usuario_id, hogar_id, conversacion_id):
        fila = (
            ConversacionModel.objects.filter(pk=conversacion_id, usuario_id=usuario_id, hogar_id=hogar_id)
            .values(*CAMPOS)
            .first()
        )
        if fila is None:
            return None
        # el estado de las propuestas, el de AHORA (pudo confirmarse después de responder): un diccionario, una consulta
        estados = dict(PropuestaModel.objects.filter(conversacion_id=conversacion_id).values_list("id", "estado"))
        mensajes = MensajeModel.objects.filter(conversacion_id=conversacion_id, visible=True).order_by("id")
        return ConversacionDetalle(
            _listada(fila),
            tuple(
                MensajeVisible(
                    m.pk,
                    m.rol,
                    m.texto,
                    _con_estados(m.datos, estados),
                    m.incompleto,
                    m.nombre_adjunto,
                    m.creado,
                )
                for m in mensajes
            ),
        )

    def carpetas(self, usuario_id, hogar_id):
        filas = (
            CarpetaModel.objects.filter(usuario_id=usuario_id, hogar_id=hogar_id)
            .annotate(n=Count("conversaciones"))
            .order_by("nombre")
        )
        return tuple(CarpetaListada(c.pk, c.nombre, c.n) for c in filas)


def _con_estados(datos: dict, estados: dict[int, str]) -> dict:
    if not datos.get("propuestas"):
        return datos
    return {**datos, "propuestas": [{**p, "estado": estados.get(p["id"], "descartada")} for p in datos["propuestas"]]}
