"""Módulo 94: el contexto de una pregunta sale de la sesión, nunca del modelo."""

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.tests.fakes.membresias_fake import MembresiasFake
from asistente.tests.fakes.mundo import ANA, CASA, HOY, contexto
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.tests.fakes.reloj_fake import RelojFake


def test_quien_no_es_miembro_no_pregunta_por_ese_hogar():
    with pytest.raises(SinPermisoException, match="El hogar no existe o no eres miembro"):
        ContextoPregunta.abrir(usuario_id=99, hogar_id=CASA.id, membresias=MembresiasFake(), reloj=RelojFake(HOY))


@pytest.mark.parametrize("rol", ["admin", "miembro", "lector"])
def test_el_agente_solo_lee_aunque_seas_administrador(rol):
    c = contexto(replace(CASA, rol=rol))
    assert (c.actor.usuario_id, c.actor.rol) == (ANA, "lector")


def test_hoy_es_el_del_hogar_no_el_del_servidor():
    # 31 de octubre, 23:30 UTC: en Madrid ya es 1 de noviembre; en Nueva York, todavía 31
    tarde = datetime(2026, 10, 31, 23, 30, tzinfo=UTC)
    assert str(contexto(ahora=tarde).hoy) == "2026-11-01"
    assert str(contexto(replace(CASA, zona_horaria="America/New_York"), ahora=tarde).hoy) == "2026-10-31"
