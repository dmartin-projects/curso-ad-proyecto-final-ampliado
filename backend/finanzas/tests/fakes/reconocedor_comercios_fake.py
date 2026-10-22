# finanzas/tests/fakes/reconocedor_comercios_fake.py — IReconocedorComercios en memoria (módulos 87 y 88)
from collections import Counter

from core.domain.services.normalizacion import normalizar
from finanzas.application.ports.i_reconocedor_comercios import IReconocedorComercios


class ReconocedorComerciosFake(IReconocedorComercios):
    """Reconoce por "el nombre conocido está dentro del texto". La categoría habitual sale de los movimientos
    revisados del fake de movimientos, como en el ORM (por eso recibe los otros dos fakes)."""

    def __init__(self, movimientos=None, categorias=None, **comercios: int):  # mercadona=100
        self._comercios = {normalizar(nombre): (pk, nombre.capitalize()) for nombre, pk in comercios.items()}
        self._movimientos, self._categorias = movimientos, categorias
        self.creados: list[str] = []

    def reconocer(self, texto):
        normalizado = normalizar(texto)
        return next((pk for nombre, (pk, _) in self._comercios.items() if nombre and nombre in normalizado), None)

    # ── Módulo 88 ──
    def reconocer_o_crear(self, nombre, nif=""):
        if not normalizar(nombre):
            return None
        if (pk := self.reconocer(nombre)) is not None:
            return pk, next(n for p, n in self._comercios.values() if p == pk)
        pk = 1000 + len(self.creados)
        self._comercios[normalizar(nombre)] = (pk, nombre.strip())
        self.creados.append(nombre.strip())
        return pk, nombre.strip()

    def categoria_habitual(self, hogar_id, comercio_id, sugerida=""):
        if comercio_id is not None and self._movimientos is not None:
            veces = Counter(
                m.categoria_id
                for m in self._movimientos.todos()
                if m.hogar_id == hogar_id and m.comercio_id == comercio_id and m.categoria_id and m.revisado
            )
            if veces:
                return min(veces, key=lambda c: (-veces[c], c))  # la más usada; a igualdad, la de id menor
        if sugerida and self._categorias is not None:
            return next(
                (c.id for c in self._categorias.del_hogar(hogar_id) if c.nombre.lower() == sugerida.lower()), None
            )
        return None
