# tickets/tests/fakes/gastos_fake.py — IGastos en memoria: finanzas, vista desde los tickets (módulo 88)
from tickets.application.ports.i_gastos import IGastos


class GastosFake(IGastos):
    """finanzas, vista desde los tickets. Guarda los gastos como dicts; `revisado` decide si se pueden descartar."""

    def __init__(self, *cuentas: tuple[int, int], categorias=("Supermercado", "Ocio")):
        self.cuentas, self.categorias = set(cuentas), list(categorias)
        self.gastos: dict[int, dict] = {}

    def nombres_de_categorias(self, hogar_id):
        return list(self.categorias)

    def existe_cuenta(self, hogar_id, cuenta_id):
        return (hogar_id, cuenta_id) in self.cuentas

    def _nuevo(self, **gasto) -> int:
        pk = len(self.gastos) + 1
        self.gastos[pk] = gasto
        return pk

    def apuntar(
        self, *, hogar_id, actor, cuenta_id, fecha, total, concepto, comercio, nif, categoria_sugerida, revisado
    ):
        return self._nuevo(
            hogar_id=hogar_id,
            creado_por=actor.usuario_id,
            fecha=fecha,
            total=total,
            concepto=concepto,
            revisado=revisado,
            de="ticket",
        )

    def registrar(self, *, hogar_id, actor, cuenta_id, fecha, total, concepto, categoria_id):
        return self._nuevo(
            hogar_id=hogar_id,
            creado_por=actor.usuario_id,
            fecha=fecha,
            total=total,
            concepto=concepto,
            categoria_id=categoria_id,
            revisado=True,
            de="persona",
        )

    def corregir(self, *, hogar_id, actor, movimiento_id, fecha, total, concepto, categoria_id):
        self.gastos[movimiento_id] |= {
            "fecha": fecha,
            "total": total,
            "concepto": concepto,
            "categoria_id": categoria_id,
            "revisado": True,
        }

    def descartar(self, *, hogar_id, actor, movimiento_id):
        if movimiento_id in self.gastos and not self.gastos[movimiento_id]["revisado"]:
            del self.gastos[movimiento_id]
            return True
        return False
