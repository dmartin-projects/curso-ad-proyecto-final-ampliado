# finanzas/tests/fakes/categoria_command_repository_fake.py — ICategoriaCommandRepository en memoria (módulo 87)
from finanzas.domain.exceptions.categoria_duplicada_exception import CategoriaDuplicadaException
from finanzas.domain.exceptions.categoria_no_encontrada_exception import CategoriaNoEncontradaException
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia


class CategoriaCommandRepositoryFake(AlmacenEnMemoria, ICategoriaCommandRepository):
    def obtener(self, hogar_id, categoria_id):
        c = self._datos.get(categoria_id)
        if c is None or c.hogar_id != hogar_id:
            raise CategoriaNoEncontradaException()
        return copia(c)

    def del_hogar(self, hogar_id):
        return sorted((copia(c) for c in self._datos.values() if c.hogar_id == hogar_id), key=lambda c: c.orden)

    def tiene_hijas(self, categoria_id):
        return any(c.padre_id == categoria_id for c in self._datos.values())

    def guardar(self, categoria):
        clave = (categoria.hogar_id, categoria.padre_id, categoria.nombre)
        if any((c.hogar_id, c.padre_id, c.nombre) == clave and c.id != categoria.id for c in self._datos.values()):
            raise CategoriaDuplicadaException()  # la UniqueConstraint categoria_unica_por_nivel
        self._asignar_id(categoria)
        self._datos[categoria.id] = copia(categoria)

    def crear_varias(self, categorias):
        for c in categorias:
            self.guardar(c)

    def guardar_orden(self, categorias):
        for c in categorias:
            self._datos[c.id].orden = c.orden

    def eliminar(self, categoria):
        for hija in [c.id for c in self._datos.values() if c.padre_id == categoria.id]:  # CASCADE
            self._datos.pop(hija)
        self._datos.pop(categoria.id, None)
