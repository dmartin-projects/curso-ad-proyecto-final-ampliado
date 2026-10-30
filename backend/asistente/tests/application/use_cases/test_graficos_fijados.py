"""Módulo 97: un gráfico fijado se guarda como su consulta y se recalcula al mirarlo, con el Actor de quien mira."""

import pytest

from asistente.application.chat.calculadora_de_graficos import CalculadoraDeGraficos
from asistente.application.fijar_grafico_use_case.dtos.fijar_grafico_input_dto import FijarGraficoInputDTO
from asistente.application.fijar_grafico_use_case.fijar_grafico_use_case import FijarGraficoUseCase
from asistente.application.listar_graficos_fijados_use_case.dtos.listar_graficos_fijados_input_dto import (
    ListarGraficosFijadosInputDTO,
)
from asistente.application.listar_graficos_fijados_use_case.listar_graficos_fijados_use_case import (
    ListarGraficosFijadosUseCase,
)
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.grafico_fijado_repositorio_fake import GraficoFijadoRepositorioFake
from asistente.tests.fakes.mundo import ANA, HOGAR, SEPTIEMBRE, Mundo, membresias, reloj
from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from core.domain.exceptions.validacion_exception import ValidacionException
from core.domain.vo.actor import Actor
from core.tests.fakes.unidad_de_trabajo_fake import UnidadDeTrabajoFake

POR_CATEGORIA = {
    "tipo": "barras",
    "titulo": "Septiembre",
    "fuente": "gasto_por_categoria",
    "argumentos": {"mes": "2026-09"},
}


@pytest.fixture
def montaje():
    mundo, repo = Mundo(), GraficoFijadoRepositorioFake()
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(
        SEPTIEMBRE, "500", categorias=[("Ocio", "100"), ("Casa", "400")]
    )
    calculadora = CalculadoraDeGraficos(mundo.catalogo())
    comun = {"calculadora": calculadora, "membresias": membresias(), "reloj": reloj()}
    fijar = FijarGraficoUseCase(graficos=repo, uow=UnidadDeTrabajoFake(repo), **comun)
    listar = ListarGraficosFijadosUseCase(consultas=repo, **comun)
    return mundo, fijar, listar


def test_se_fija_y_se_recalcula_al_mirarlo(montaje):
    mundo, fijar, listar = montaje
    fijado = fijar.ejecutar(FijarGraficoInputDTO(HOGAR, Actor(ANA, Rol.MIEMBRO), POR_CATEGORIA))
    assert fijado.grafico["series"][0]["valores"] == [100.0, 400.0]
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, "900", categorias=[("Ocio", "900")])
    (leido,) = listar.ejecutar(ListarGraficosFijadosInputDTO(HOGAR, Actor(ANA, Rol.LECTOR)))
    assert (leido.grafico["etiquetas"], leido.grafico["series"][0]["valores"]) == (["Ocio"], [900.0])
    assert mundo.finanzas.consultas[-1][1].rol == Rol.LECTOR  # con el Actor del agente, también aquí


def test_fijar_cambia_el_dashboard_de_todos_un_lector_no(montaje):
    _, fijar, _ = montaje
    with pytest.raises(SinPermisoException):
        fijar.ejecutar(FijarGraficoInputDTO(HOGAR, Actor(ANA, Rol.LECTOR), POR_CATEGORIA))


def test_lo_que_no_se_puede_dibujar_no_se_fija(montaje):
    _, fijar, _ = montaje
    with pytest.raises(ValidacionException, match="no tiene datos que dibujar"):
        fijar.ejecutar(
            FijarGraficoInputDTO(HOGAR, Actor(ANA, Rol.ADMIN), {**POR_CATEGORIA, "argumentos": {"mes": "2026-01"}})
        )
    with pytest.raises(ValidacionException, match="no se puede dibujar"):
        fijar.ejecutar(
            FijarGraficoInputDTO(HOGAR, Actor(ANA, Rol.ADMIN), {**POR_CATEGORIA, "fuente": "buscar_movimientos"})
        )


def test_uno_que_ya_no_se_puede_calcular_sale_con_su_motivo(montaje):
    mundo, fijar, listar = montaje
    fijar.ejecutar(FijarGraficoInputDTO(HOGAR, Actor(ANA, Rol.ADMIN), POR_CATEGORIA))
    mundo.finanzas.resumenes.clear()
    (leido,) = listar.ejecutar(ListarGraficosFijadosInputDTO(HOGAR, Actor(ANA, Rol.LECTOR)))
    assert (leido.grafico, leido.error) == (None, "Esa consulta no tiene datos que dibujar: prueba con otro periodo.")
