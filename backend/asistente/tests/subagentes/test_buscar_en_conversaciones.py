"""Módulo 105: la memoria de las conversaciones, contra PostgreSQL: solo las de quien pregunta en ese hogar, solo lo
visible, sin la conversación de ahora, y con tildes o sin ellas."""

from dataclasses import replace

import pytest

from asistente.application.tools.buscar_en_conversaciones_tool import BuscarEnConversacionesTool
from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
from asistente.domain.vo.resultado_tool import ResultadoTool
from asistente.infrastructure import container
from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
    ConversacionCommandRepositoryORM,
)
from asistente.infrastructure.database.repositories.conversacion_query_service_orm import ConversacionQueryServiceORM
from conftest import MembresiaFactory, UsuarioFactory

pytestmark = pytest.mark.django_db


def conversacion(usuario_id: int, hogar_id: int, *textos: str, titulo: str = "") -> int:
    repo = ConversacionCommandRepositoryORM()
    c = Conversacion(usuario_id, hogar_id)
    if titulo:
        c.titular(titulo)
    repo.guardar(c)
    mensajes = [MensajeDeConversacion(Mensaje.usuario(t), visible=True, texto=t) for t in textos]
    repo.anadir(c.id, mensajes)
    return c.id


def buscar(contexto, texto: str) -> dict:
    tool = BuscarEnConversacionesTool(consultas=ConversacionQueryServiceORM())
    return tool.ejecutar(contexto, tool.validar(f'{{"texto": "{texto}"}}'))


def test_lo_que_se_dijo_otro_dia_con_tildes_o_sin_ellas(casa):
    ana, hogar = casa
    conversacion(ana.pk, hogar.pk, "En marzo nos vamos de viaje a Londres, unos 900 € en total.", titulo="El viaje")
    r = buscar(container.contexto(ana.pk, hogar.pk), "londres")
    assert r["encontradas"] == 1
    assert r["conversaciones"][0]["titulo"] == "El viaje"
    assert r["conversaciones"][0]["dice"] == ["En marzo nos vamos de viaje a Londres, unos 900 € en total."]
    assert buscar(container.contexto(ana.pk, hogar.pk), "viaje a Londres")["encontradas"] == 1


def test_ni_las_de_otro_miembro_ni_la_de_ahora_ni_lo_que_no_se_ve(casa):
    ana, hogar = casa
    luis = UsuarioFactory()
    MembresiaFactory(hogar=hogar, usuario=luis, rol="editor")
    conversacion(luis.pk, hogar.pk, "Lo de la hipoteca, que no se entere nadie.")
    ahora = conversacion(ana.pk, hogar.pk, "¿Qué te dije de la hipoteca?")
    repo = ConversacionCommandRepositoryORM()
    otra = Conversacion(ana.pk, hogar.pk)
    repo.guardar(otra)
    repo.anadir(
        otra.id,
        [  # el resultado de una tool no es visible: no se busca en él
            MensajeDeConversacion(Mensaje.modelo(llamadas=(LlamadaTool("1", "buscar_movimientos", "{}"),))),
            MensajeDeConversacion(Mensaje.de_tools((ResultadoTool("1", "buscar_movimientos", '"hipoteca"'),))),
        ],
    )
    contexto = replace(container.contexto(ana.pk, hogar.pk), conversacion_id=ahora)
    assert buscar(contexto, "hipoteca") == {
        "encontradas": 0,
        "nota": "No habéis hablado de eso en otras conversaciones.",
    }


def test_un_fragmento_alrededor_y_como_mucho_tres_conversaciones(casa):
    ana, hogar = casa
    largo = "Antes de nada. " * 20 + "El seguro del coche sube en enero. " + "Y luego más cosas. " * 20
    for _ in range(4):
        conversacion(ana.pk, hogar.pk, largo)
    r = buscar(container.contexto(ana.pk, hogar.pk), "seguro del coche")
    assert r["encontradas"] == 3
    (fragmento,) = r["conversaciones"][0]["dice"]
    assert fragmento.startswith("…") and fragmento.endswith("…") and "seguro del coche" in fragmento
    assert len(fragmento) <= 162
