"""Módulo 97: los repositorios del chat contra PostgreSQL. El historial vuelve tal cual (el formato del dominio) y sin
las preguntas incompletas; las carpetas no se repiten; una conversación borrada se lleva sus mensajes."""

import pytest

from asistente.domain.bo.carpeta import Carpeta
from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.exceptions.carpeta_repetida_exception import CarpetaRepetidaException
from asistente.domain.exceptions.conversacion_no_encontrada_exception import ConversacionNoEncontradaException
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
from asistente.domain.vo.resultado_tool import ResultadoTool
from asistente.infrastructure.database.repositories.carpeta_command_repository_orm import CarpetaCommandRepositoryORM
from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
    ConversacionCommandRepositoryORM,
)
from asistente.infrastructure.database.repositories.conversacion_query_service_orm import ConversacionQueryServiceORM
from asistente.models import Mensaje as MensajeModel

pytestmark = pytest.mark.django_db

HISTORIAL = (
    Mensaje.usuario("¿Cuánto en septiembre?"),
    Mensaje.modelo(llamadas=(LlamadaTool("fc_1", "resumen_mes", '{"mes":"2026-09"}'),)),
    Mensaje.de_tools((ResultadoTool("fc_1", "resumen_mes", '{"gastos":"776.59"}'),)),
    Mensaje.modelo(texto="776,59 €."),
)


def test_el_historial_vuelve_igual_y_sin_lo_incompleto(casa):
    ana, hogar = casa
    repo = ConversacionCommandRepositoryORM()
    c = Conversacion(ana.pk, hogar.pk)
    repo.guardar(c)
    ids = repo.anadir(c.id, [MensajeDeConversacion(m, visible=m.rol == "usuario") for m in HISTORIAL])
    assert repo.historial(c.id) == HISTORIAL
    (cancelada,) = repo.anadir(c.id, [MensajeDeConversacion(Mensaje.usuario("¿Y en agosto?"), visible=True)])
    repo.marcar_incompleto(cancelada, "cancelada")
    assert repo.historial(c.id) == HISTORIAL and ids == sorted(ids)
    detalle = ConversacionQueryServiceORM().detalle(ana.pk, hogar.pk, c.id)
    assert [(m.texto, m.incompleto) for m in detalle.mensajes] == [("", False), ("", True)]  # los visibles


def test_solo_la_de_esa_persona_en_ese_hogar(casa):
    ana, hogar = casa
    repo = ConversacionCommandRepositoryORM()
    c = Conversacion(ana.pk, hogar.pk)
    repo.guardar(c)
    with pytest.raises(ConversacionNoEncontradaException):
        repo.obtener(ana.pk + 1000, hogar.pk, c.id)
    assert ConversacionQueryServiceORM().detalle(ana.pk + 1000, hogar.pk, c.id) is None


def test_carpetas_sin_repetir_y_al_borrarla_las_conversaciones_se_quedan(casa):
    ana, hogar = casa
    carpetas, repo = CarpetaCommandRepositoryORM(), ConversacionCommandRepositoryORM()
    viaje = Carpeta(ana.pk, hogar.pk, "Viaje")
    carpetas.guardar(viaje)
    with pytest.raises(CarpetaRepetidaException):
        carpetas.guardar(Carpeta(ana.pk, hogar.pk, "Viaje"))
    c = Conversacion(ana.pk, hogar.pk, carpeta_id=viaje.id)
    repo.guardar(c)
    carpetas.eliminar(viaje)
    assert repo.obtener(ana.pk, hogar.pk, c.id).carpeta_id is None


def test_borrar_una_conversacion_se_lleva_sus_mensajes(casa):
    ana, hogar = casa
    repo = ConversacionCommandRepositoryORM()
    c = Conversacion(ana.pk, hogar.pk)
    repo.guardar(c)
    repo.anadir(c.id, [MensajeDeConversacion(HISTORIAL[0], visible=True)])
    repo.eliminar(c)
    assert not MensajeModel.objects.filter(conversacion_id=c.id).exists()


def test_los_archivos_de_una_conversacion_adjuntos_y_exportaciones(casa):
    ana, hogar = casa
    repo = ConversacionCommandRepositoryORM()
    c = Conversacion(ana.pk, hogar.pk)
    repo.guardar(c)
    repo.anadir(
        c.id,
        [
            MensajeDeConversacion(HISTORIAL[0], visible=True, adjunto="asistente/1/foto", nombre_adjunto="t.jpg"),
            MensajeDeConversacion(
                HISTORIAL[3], visible=True, datos={"archivos": [{"nombre": "m.csv", "ruta": "asistente/1/e/m"}]}
            ),
        ],
    )
    assert repo.archivos(c.id) == ("asistente/1/foto", "asistente/1/e/m")
    pregunta_id, _ = repo.anadir(c.id, [MensajeDeConversacion(HISTORIAL[0], visible=True)] * 2)
    repo.ligar_archivo(pregunta_id, "asistente/1/e/n")
    repo.ligar_archivo(pregunta_id, "asistente/1/e/m")  # el de una pregunta que termina, también en la respuesta
    assert repo.archivos(c.id) == ("asistente/1/foto", "asistente/1/e/m", "asistente/1/e/n")


def test_la_lista_las_mas_recientes_primero(casa):
    ana, hogar = casa
    repo = ConversacionCommandRepositoryORM()
    vieja, nueva = Conversacion(ana.pk, hogar.pk, "Vieja"), Conversacion(ana.pk, hogar.pk, "Nueva")
    repo.guardar(vieja)
    repo.guardar(nueva)
    repo.guardar(vieja)  # una pregunta nueva en la vieja: sube
    assert [c.titulo for c in ConversacionQueryServiceORM().listar(ana.pk, hogar.pk)] == ["Vieja", "Nueva"]


def test_la_marca_de_terceros_se_guarda_con_la_conversacion(casa):
    """Módulo 102: la pregunta siguiente la lee de aquí."""
    ana, hogar = casa
    repo = ConversacionCommandRepositoryORM()
    c = Conversacion(ana.pk, hogar.pk)
    repo.guardar(c)
    assert not repo.obtener(ana.pk, hogar.pk, c.id).con_terceros
    c.marcar_con_terceros()
    repo.guardar(c)
    assert repo.obtener(ana.pk, hogar.pk, c.id).con_terceros
