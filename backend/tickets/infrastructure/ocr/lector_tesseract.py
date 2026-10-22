# tickets/infrastructure/ocr/lector_tesseract.py — ILectorDeTickets: texto con Tesseract (imágenes) o la capa de
# texto del PDF (módulos 74 y 88)
#
# Todo es local y gratis. Se ejecuta en el worker de la cola "ocr" (CPU), nunca en la petición. `Lectura` y
# MIN_CARACTERES son del dominio; LectorTesseract, al final, es el adapter.

import io

import pypdfium2 as pdfium
import pytesseract
from opentelemetry import trace
from PIL import Image, ImageOps

from tickets.application.ports.i_lector_de_tickets import ILectorDeTickets
from tickets.domain.vo.lectura import MIN_CARACTERES, Lectura

LADO_MINIMO = 1500  # Tesseract lee mal el texto pequeño: se amplía la imagen
tracer = trace.get_tracer("gastos.tickets")  # módulo 84: sin OpenTelemetry activo, no hace nada


def _preparar(imagen: Image.Image) -> Image.Image:
    imagen = ImageOps.exif_transpose(imagen)  # fotos del móvil giradas
    imagen = ImageOps.grayscale(imagen)
    imagen = ImageOps.autocontrast(imagen, cutoff=1)
    if (lado := min(imagen.size)) < LADO_MINIMO:
        factor = LADO_MINIMO / lado
        imagen = imagen.resize((round(imagen.width * factor), round(imagen.height * factor)), Image.Resampling.LANCZOS)
    return imagen


def _png(imagen: Image.Image) -> bytes:
    salida = io.BytesIO()
    imagen.save(salida, format="PNG", optimize=True)
    return salida.getvalue()


def leer_imagen(contenido: bytes) -> Lectura:
    with Image.open(io.BytesIO(contenido)) as original:
        imagen = _preparar(original)
    # --psm 4: una columna de texto de tamaños variables (justo un ticket)
    texto = pytesseract.image_to_string(imagen, lang="spa", config="--psm 4", timeout=60)
    return Lectura(texto=texto, imagen_png=_png(imagen))


def leer_pdf(contenido: bytes) -> Lectura:
    pdf = pdfium.PdfDocument(contenido)
    try:
        pagina = pdf[0]
        texto = pagina.get_textpage().get_text_range()  # ticket electrónico: ya trae texto
        imagen = pagina.render(scale=200 / 72).to_pil()  # 200 ppp
        if len(texto.strip()) < MIN_CARACTERES:  # PDF escaneado: no hay capa de texto → OCR
            return leer_imagen(_png(imagen))
        return Lectura(texto=texto, imagen_png=_png(imagen))
    finally:
        pdf.close()


def leer(contenido: bytes, tipo: str) -> Lectura:
    return leer_pdf(contenido) if tipo == "application/pdf" else leer_imagen(contenido)


class LectorTesseract(ILectorDeTickets):
    """El span "ticket.ocr" (módulo 84) es de este adapter: la telemetría es infraestructura."""

    def leer(self, contenido: bytes, tipo_archivo: str) -> Lectura:
        with tracer.start_as_current_span("ticket.ocr") as span:
            lectura = leer(contenido, tipo_archivo)  # la función del módulo (los tests la sustituyen: es lenta)
            # Atributos para filtrar en Tempo: cuántos caracteres y si sirvió. NUNCA el texto (datos personales)
            span.set_attributes(
                {"ticket.tipo": tipo_archivo, "ocr.caracteres": len(lectura.texto), "ocr.util": lectura.es_util}
            )
        return lectura
