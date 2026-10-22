# informes/tests/fakes/maquetador_fake.py — IMaquetador: un «PDF» de unos bytes (módulo 88)
from informes.application.ports.i_maquetador import IMaquetador


class MaquetadorFake(IMaquetador):
    def pdf(self, hogar_id, mes, idioma=None):
        return b"%PDF-1.7 " + str(mes).encode()
