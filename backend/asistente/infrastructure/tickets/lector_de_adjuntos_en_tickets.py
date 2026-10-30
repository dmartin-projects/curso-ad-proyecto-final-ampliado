# asistente/infrastructure/tickets/lector_de_adjuntos_en_tickets.py — ILectorDeAdjuntos con el OCR de tickets (módulo 97)
#
# Anti-corruption layer: el asistente pide "el texto de este archivo"; el OCR (Tesseract, o la capa de texto del PDF,
# módulo 74) es de tickets y se pide a su contenedor. Corre dentro de la petición del chat (en el hilo de la respuesta
# en streaming): la persona espera la respuesta de todos modos, y la interfaz dice "Leyendo el adjunto".
from asistente.application.ports.i_lector_de_adjuntos import ILectorDeAdjuntos
from tickets.infrastructure import container as tickets


class LectorDeAdjuntosEnTickets(ILectorDeAdjuntos):
    def leer(self, contenido, tipo):
        return tickets.lector_de_tickets().leer(contenido, tipo).texto
