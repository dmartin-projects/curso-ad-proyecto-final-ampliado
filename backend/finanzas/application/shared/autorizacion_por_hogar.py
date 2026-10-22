# finanzas/application/shared/autorizacion_por_hogar.py — lo que comparten los use cases de finanzas (módulo 87)
from finanzas.domain.bo.categoria import Categoria
from finanzas.domain.exceptions.categoria_no_encontrada_exception import CategoriaNoEncontradaException
from finanzas.domain.exceptions.cuenta_no_encontrada_exception import CuentaNoEncontradaException
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


def exigir_cuenta(cuentas: ICuentaCommandRepository, hogar_id: int, cuenta_id: int) -> None:
    """Autorización por hogar: un id que llega del exterior tiene que ser de ESTE hogar."""
    if not cuentas.existe(hogar_id, cuenta_id):
        raise CuentaNoEncontradaException()


def exigir_categoria(
    categorias: ICategoriaCommandRepository, hogar_id: int, categoria_id: int, campo: str
) -> Categoria:
    try:
        return categorias.obtener(hogar_id, categoria_id)
    except CategoriaNoEncontradaException:
        # como error del formulario: 400 en errors.<campo>
        raise CategoriaNoEncontradaException(campo=campo) from None
