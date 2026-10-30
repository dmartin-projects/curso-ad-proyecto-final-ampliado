"""Módulo 97: los adapters del chat hacia otras apps: el CSV de finanzas al almacén y el OCR de tickets."""

import csv
import io
import shutil
from datetime import date

import pytest

from asistente.domain.vo.filtro_de_movimientos import FiltroDeMovimientos
from asistente.infrastructure.finanzas.exportador_en_finanzas import ExportadorEnFinanzas
from asistente.infrastructure.tickets.lector_de_adjuntos_en_tickets import LectorDeAdjuntosEnTickets
from asistente.tests.fakes.almacen_de_archivos_fake import AlmacenDeArchivosFake
from core.domain.enums.rol import Rol
from core.domain.vo.actor import Actor

pytestmark = pytest.mark.django_db


def test_el_csv_de_un_filtro_el_mismo_que_el_de_la_pantalla(casa):
    ana, hogar = casa
    almacen = AlmacenDeArchivosFake()
    filtro = FiltroDeMovimientos(date(2026, 9, 1), date(2026, 9, 30), texto="Mercadona")
    a = ExportadorEnFinanzas(almacen=almacen).exportar(Actor(ana.pk, Rol.LECTOR), hogar.pk, filtro, "m.csv")
    assert (a.nombre, a.filas) == ("m.csv", 2)
    filas = list(csv.reader(io.StringIO(almacen.archivos[a.ruta].decode("utf-8-sig")), delimiter=";"))
    assert filas[0] == ["fecha", "concepto", "importe", "cuenta", "categoría", "etiquetas"]
    assert [f[2] for f in filas[1:]] == ["-121,35", "-287,90"]


def test_sin_filas_no_hay_archivo(casa):
    ana, hogar = casa
    almacen = AlmacenDeArchivosFake()
    filtro = FiltroDeMovimientos(date(2026, 9, 1), date(2026, 9, 30), texto="nada de nada")
    a = ExportadorEnFinanzas(almacen=almacen).exportar(Actor(ana.pk, Rol.LECTOR), hogar.pk, filtro, "m.csv")
    assert (a.filas, a.ruta, almacen.archivos) == (0, "", {})


def test_un_concepto_que_parece_una_formula_no_se_ejecuta_en_la_hoja_de_calculo(casa):
    """CSV injection: el concepto lo escribe el banco (o quien le hizo la transferencia)."""
    from conftest import MovimientoFactory

    ana, hogar = casa
    MovimientoFactory(cuenta__hogar=hogar, fecha=date(2026, 9, 3), concepto='=HYPERLINK("https://x.example","Ver")')
    almacen = AlmacenDeArchivosFake()
    filtro = FiltroDeMovimientos(date(2026, 9, 3), date(2026, 9, 3), texto="HYPERLINK")
    a = ExportadorEnFinanzas(almacen=almacen).exportar(Actor(ana.pk, Rol.LECTOR), hogar.pk, filtro, "m.csv")
    (_, fila) = list(csv.reader(io.StringIO(almacen.archivos[a.ruta].decode("utf-8-sig")), delimiter=";"))
    assert fila[1] == '\'=HYPERLINK("https://x.example","Ver")'
    assert fila[2].startswith("-")  # el importe, un número negativo tal cual


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="Tesseract no está instalado")
def test_el_ocr_de_tickets_lee_el_adjunto():
    from tickets.tests.conftest import imagen_ticket

    assert "MERCADONA" in LectorDeAdjuntosEnTickets().leer(imagen_ticket(), "image/jpeg")
