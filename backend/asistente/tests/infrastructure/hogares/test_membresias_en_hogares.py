"""Módulo 94: el anti-corruption layer hacia hogares y su fake cumplen el mismo contrato."""

import pytest

from asistente.domain.read_models.hogar_del_usuario import HogarDelUsuario
from asistente.infrastructure.hogares.membresias_en_hogares import MembresiasEnHogares
from asistente.tests.fakes.membresias_fake import MembresiasFake


@pytest.fixture(params=["fake", "orm"])
def membresias(request, casa):
    ana, hogar = casa
    if request.param == "orm":
        return MembresiasEnHogares(), ana, hogar
    datos = HogarDelUsuario(hogar.pk, "Casa de Ana y Luis", "EUR", "Europe/Madrid", "admin")
    return MembresiasFake({(ana.pk, hogar.pk): datos}), ana, hogar


def test_el_hogar_de_un_miembro_con_su_rol(membresias):
    m, ana, hogar = membresias
    assert m.hogar_de(ana.pk, hogar.pk) == HogarDelUsuario(
        hogar.pk, "Casa de Ana y Luis", "EUR", "Europe/Madrid", "admin"
    )


def test_quien_no_es_miembro_no_lo_ve(membresias):
    m, ana, hogar = membresias
    assert m.hogar_de(ana.pk + 1000, hogar.pk) is None
    assert m.hogar_de(ana.pk, hogar.pk + 1000) is None
