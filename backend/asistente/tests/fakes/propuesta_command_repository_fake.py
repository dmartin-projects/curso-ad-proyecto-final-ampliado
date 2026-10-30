# asistente/tests/fakes/propuesta_command_repository_fake.py (módulo 97)
from asistente.domain.exceptions.propuesta_no_encontrada_exception import PropuestaNoEncontradaException
from asistente.domain.repositories.i_propuesta_command_repository import IPropuestaCommandRepository
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia


class PropuestaCommandRepositoryFake(AlmacenEnMemoria, IPropuestaCommandRepository):
    def __init__(self):
        super().__init__()
        self.bloqueadas: list[int] = []

    def obtener(self, usuario_id, hogar_id, propuesta_id, bloquear=False):
        p = self._datos.get(propuesta_id)
        if p is None or (p.usuario_id, p.hogar_id) != (usuario_id, hogar_id):
            raise PropuestaNoEncontradaException()
        if bloquear:
            self.bloqueadas.append(propuesta_id)
        return copia(p)

    def guardar(self, propuesta):
        self._asignar_id(propuesta)
        self._datos[propuesta.id] = copia(propuesta)
