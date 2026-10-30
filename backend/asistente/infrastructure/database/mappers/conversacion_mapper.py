# asistente/infrastructure/database/mappers/conversacion_mapper.py (módulo 97)
from asistente.domain.bo.carpeta import Carpeta
from asistente.domain.bo.conversacion import Conversacion
from asistente.infrastructure.database.models.carpeta_model import Carpeta as CarpetaModel
from asistente.infrastructure.database.models.conversacion_model import Conversacion as ConversacionModel


def conversacion_a_bo(fila: ConversacionModel) -> Conversacion:
    return Conversacion(
        usuario_id=fila.usuario_id,
        hogar_id=fila.hogar_id,
        titulo=fila.titulo,
        titulo_manual=fila.titulo_manual,
        carpeta_id=fila.carpeta_id,
        id=fila.pk,
        resumen=fila.resumen,
        resumido_hasta=fila.resumido_hasta,
    )


def carpeta_a_bo(fila: CarpetaModel) -> Carpeta:
    return Carpeta(usuario_id=fila.usuario_id, hogar_id=fila.hogar_id, nombre=fila.nombre, id=fila.pk)
