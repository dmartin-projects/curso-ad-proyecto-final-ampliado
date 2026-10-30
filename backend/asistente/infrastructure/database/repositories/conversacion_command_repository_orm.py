# asistente/infrastructure/database/repositories/conversacion_command_repository_orm.py (módulos 97 y 99)
from asistente.domain.exceptions.conversacion_no_encontrada_exception import ConversacionNoEncontradaException
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from asistente.domain.services.intercambios import emparejar
from asistente.infrastructure.database.mappers.conversacion_mapper import conversacion_a_bo
from asistente.infrastructure.database.mappers.mensaje_mapper import mensaje_a_json, mensaje_de_json
from asistente.infrastructure.database.models.conversacion_model import Conversacion as ConversacionModel
from asistente.infrastructure.database.models.mensaje_model import Mensaje as MensajeModel
from core.infrastructure.database.guardado import guardar_fila


class ConversacionCommandRepositoryORM(IConversacionCommandRepository):
    def obtener(self, usuario_id, hogar_id, conversacion_id):
        fila = ConversacionModel.objects.filter(pk=conversacion_id, usuario_id=usuario_id, hogar_id=hogar_id).first()
        if fila is None:
            raise ConversacionNoEncontradaException()
        return conversacion_a_bo(fila)

    def guardar(self, conversacion):
        fila = ConversacionModel(
            pk=conversacion.id,
            usuario_id=conversacion.usuario_id,
            hogar_id=conversacion.hogar_id,
            titulo=conversacion.titulo,
            titulo_manual=conversacion.titulo_manual,
            carpeta_id=conversacion.carpeta_id,
            con_terceros=conversacion.con_terceros,
        )
        guardar_fila(
            fila, ["titulo", "titulo_manual", "carpeta", "con_terceros"], {}
        )  # "actualizado" siempre: sube en la lista
        conversacion.id = fila.pk

    def guardar_resumen(self, conversacion):  # módulo 99: update() no toca "actualizado" (auto_now es de save())
        ConversacionModel.objects.filter(pk=conversacion.id).update(
            resumen=conversacion.resumen, resumido_hasta=conversacion.resumido_hasta
        )

    def eliminar(self, conversacion):
        ConversacionModel.objects.filter(pk=conversacion.id).delete()

    def antiguas(self, antes_de, limite):  # módulo 107: el índice (usuario, hogar, -actualizado) no sirve aquí
        filas = ConversacionModel.objects.filter(actualizado__lt=antes_de).order_by("actualizado")[:limite]
        return tuple(conversacion_a_bo(f) for f in filas)

    def archivos(self, conversacion_id):
        rutas = []
        for adjunto, datos in MensajeModel.objects.filter(conversacion_id=conversacion_id).values_list(
            "adjunto", "datos"
        ):
            rutas += [adjunto] if adjunto else []
            rutas += [a["ruta"] for a in (datos or {}).get("archivos", []) if a.get("ruta")]
            rutas += (datos or {}).get("exportados", [])  # los ligados a la pregunta (ligar_archivo)
        return tuple(dict.fromkeys(rutas))  # un CSV de una pregunta que termina está en los dos sitios

    def ligar_archivo(self, mensaje_id, ruta):
        # En la PREGUNTA, aparte de "archivos" (lo que la interfaz pinta con la respuesta): solo para encontrarlo
        fila = MensajeModel.objects.get(pk=mensaje_id)
        fila.datos = {**(fila.datos or {}), "exportados": [*(fila.datos or {}).get("exportados", []), ruta]}
        fila.save(update_fields=["datos"])

    def historial(self, conversacion_id, despues_de=None):
        filas = MensajeModel.objects.filter(conversacion_id=conversacion_id, incompleto=False)
        if despues_de is not None:  # módulo 99: lo anterior ya está en el resumen
            filas = filas.filter(pk__gt=despues_de)
        return tuple(mensaje_de_json(c) for c in filas.order_by("id").values_list("contenido", flat=True))

    def intercambios(self, conversacion_id, despues_de=None):
        filas = MensajeModel.objects.filter(
            conversacion_id=conversacion_id, visible=True, incompleto=False, pk__gt=despues_de or 0
        )
        return emparejar(filas.order_by("id").values_list("id", "rol", "texto"))

    def anadir(self, conversacion_id, mensajes):
        filas = MensajeModel.objects.bulk_create(
            MensajeModel(
                conversacion_id=conversacion_id,
                rol=str(m.mensaje.rol),
                contenido=mensaje_a_json(m.mensaje),
                texto=m.texto,
                visible=m.visible,
                datos=m.datos,
                adjunto=m.adjunto or "",
                nombre_adjunto=m.nombre_adjunto,
            )
            for m in mensajes
        )
        return [f.pk for f in filas]  # PostgreSQL devuelve los ids del INSERT (RETURNING)

    def marcar_incompleto(self, mensaje_id, motivo):
        MensajeModel.objects.filter(pk=mensaje_id).update(incompleto=True, motivo=motivo)
