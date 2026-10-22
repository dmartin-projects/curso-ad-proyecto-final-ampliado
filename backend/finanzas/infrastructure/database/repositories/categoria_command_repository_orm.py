# finanzas/infrastructure/database/repositories/categoria_command_repository_orm.py (módulo 87)
#
# El use case no pregunta "¿existe ya una categoría con ese nombre?" antes de guardar: guarda, y si PostgreSQL
# dice que no, este repositorio traduce la constraint (por su nombre) a CategoriaDuplicadaException.
from django.db import IntegrityError, transaction

from core.infrastructure.database.guardado import guardar_fila, nombre_constraint
from core.infrastructure.signals.red_de_seguridad import publicados_por_caso_de_uso
from finanzas.domain.bo.categoria import Categoria
from finanzas.domain.exceptions.categoria_duplicada_exception import CategoriaDuplicadaException
from finanzas.domain.exceptions.categoria_no_encontrada_exception import CategoriaNoEncontradaException
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.infrastructure.database.mappers.categoria_mapper import categoria_a_bo, categoria_a_modelo
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel

CAMPOS = ["nombre", "padre", "color", "icono", "orden", "es_ingreso"]


class CategoriaCommandRepositoryORM(ICategoriaCommandRepository):
    errores = {"categoria_unica_por_nivel": CategoriaDuplicadaException}

    def obtener(self, hogar_id: int, categoria_id: int) -> Categoria:
        fila = CategoriaModel.objects.filter(hogar_id=hogar_id, pk=categoria_id).first()
        if fila is None:
            raise CategoriaNoEncontradaException()
        return categoria_a_bo(fila)

    def del_hogar(self, hogar_id: int) -> list[Categoria]:
        return [categoria_a_bo(f) for f in CategoriaModel.objects.filter(hogar_id=hogar_id)]

    def tiene_hijas(self, categoria_id: int) -> bool:
        return CategoriaModel.objects.filter(padre_id=categoria_id).exists()

    def guardar(self, categoria: Categoria) -> None:
        fila = publicados_por_caso_de_uso(categoria_a_modelo(categoria))
        guardar_fila(fila, CAMPOS, self.errores)
        categoria.id = fila.pk

    def crear_varias(self, categorias: list[Categoria]) -> None:
        try:
            with transaction.atomic():
                filas = CategoriaModel.objects.bulk_create([categoria_a_modelo(c) for c in categorias])
        except IntegrityError as e:
            if nombre_constraint(e) in self.errores:
                raise CategoriaDuplicadaException() from e
            raise
        for categoria, fila in zip(categorias, filas, strict=True):
            categoria.id = fila.pk  # PostgreSQL devuelve los ids del INSERT (RETURNING)

    def guardar_orden(self, categorias: list[Categoria]) -> None:
        filas = [CategoriaModel(pk=c.id, orden=c.orden) for c in categorias]
        CategoriaModel.objects.bulk_update(filas, ["orden"])  # una consulta (módulo 09)

    def eliminar(self, categoria: Categoria) -> None:
        # CASCADE a las subcategorías y SET_NULL a sus movimientos: lo hace la BD, y los avisos y eventos de esos
        # movimientos los publican los receivers de pre_delete / post_delete de Categoria
        publicados_por_caso_de_uso(CategoriaModel(pk=categoria.id, hogar_id=categoria.hogar_id)).delete()
