"""El PDF del mes (módulos 78 y 88): plantilla de Django + WeasyPrint."""

from datetime import date

import pypdfium2 as pdfium
import pytest

from informes.infrastructure.pdf import maquetador_weasyprint as maquetador

pytestmark = pytest.mark.django_db
OCT = date(2026, 10, 1)


def texto_pdf(contenido: bytes) -> str:
    pdf = pdfium.PdfDocument(contenido)
    try:
        return "\n".join(p.get_textpage().get_text_range() for p in pdf)
    finally:
        pdf.close()


def test_el_pdf_lleva_el_resumen_y_los_movimientos_agrupados(hogar_con_datos):
    hogar, _ = hogar_con_datos

    contenido = maquetador.pdf(hogar, OCT, idioma="es")

    assert contenido.startswith(b"%PDF-")
    texto = texto_pdf(contenido)
    assert "Informe mensual" in texto and "Octubre 2026" in texto
    assert "Piso Ruzafa · Octubre 2026" in texto  # la cabecera de página (string-set)
    assert "1\xa0254,50 €" in texto  # gastos, con el formato español (separador de miles: espacio duro)
    assert "Muebles" in texto and "Sin categoría" in texto and "Página 1 / 1" in texto
