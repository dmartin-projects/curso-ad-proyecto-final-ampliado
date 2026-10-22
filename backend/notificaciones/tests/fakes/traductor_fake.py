# notificaciones/tests/fakes/traductor_fake.py — ITraductor: las plantillas son diccionarios (módulo 88)
from notificaciones.application.ports.i_traductor import ITraductor


class TraductorFake(ITraductor):
    """Las "plantillas" de los tests son diccionarios {idioma: texto}."""

    def traducir(self, plantilla, idioma, contexto):
        return plantilla[idioma] % contexto
