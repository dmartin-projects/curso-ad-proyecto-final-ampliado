# asistente/tests/fakes/carpeta_command_repository_fake.py (módulo 97)
from asistente.domain.exceptions.carpeta_no_encontrada_exception import CarpetaNoEncontradaException
from asistente.domain.exceptions.carpeta_repetida_exception import CarpetaRepetidaException
from asistente.domain.repositories.i_carpeta_command_repository import ICarpetaCommandRepository
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia


class CarpetaCommandRepositoryFake(AlmacenEnMemoria, ICarpetaCommandRepository):
    def obtener(self, usuario_id, hogar_id, carpeta_id):
        c = self._datos.get(carpeta_id)
        if c is None or (c.usuario_id, c.hogar_id) != (usuario_id, hogar_id):
            raise CarpetaNoEncontradaException()
        return copia(c)

    def guardar(self, carpeta):
        clave = (carpeta.usuario_id, carpeta.hogar_id, carpeta.nombre)
        if any((c.usuario_id, c.hogar_id, c.nombre) == clave and c.id != carpeta.id for c in self._datos.values()):
            raise CarpetaRepetidaException()  # la constraint asistente_carpeta_unica
        self._asignar_id(carpeta)
        self._datos[carpeta.id] = copia(carpeta)

    def eliminar(self, carpeta):
        self._datos.pop(carpeta.id, None)
