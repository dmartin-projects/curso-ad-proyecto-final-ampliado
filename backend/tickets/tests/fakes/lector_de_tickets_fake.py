# tickets/tests/fakes/lector_de_tickets_fake.py — ILectorDeTickets: devuelve el texto que se le dé (módulo 88)
from tickets.application.ports.i_lector_de_tickets import ILectorDeTickets
from tickets.domain.vo.lectura import Lectura

# más de 40 caracteres: es útil
TEXTO = "MERCADONA S.A.\nNIF A-46103834\nLECHE 2 x 0,95   1,90\nTOTAL   4,85"


class LectorDeTicketsFake(ILectorDeTickets):
    def __init__(self, texto=TEXTO):
        self.texto, self.lecturas = texto, 0

    def leer(self, contenido, tipo_archivo):
        self.lecturas += 1
        return Lectura(self.texto, imagen_png=b"\x89PNG")
