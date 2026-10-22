# importaciones/tests/fakes/movimientos_fake.py — IMovimientos en memoria: finanzas, vista desde las importaciones (módulo 88)
from importaciones.application.ports.i_movimientos import IMovimientos
from importaciones.domain.vo.candidato import Candidato


class MovimientosFake(IMovimientos):
    """finanzas, vista desde las importaciones: {id: {"cuenta", "fecha", "importe", "huella", "creado_por"}}."""

    def __init__(self, *cuentas):
        self.cuentas = set(cuentas)  # (hogar_id, cuenta_id)
        self.movimientos: dict[int, dict] = {}

    def nuevo(self, cuenta_id, fecha, importe, huella="") -> int:
        pk = len(self.movimientos) + 1000
        self.movimientos[pk] = {"cuenta": cuenta_id, "fecha": fecha, "importe": importe, "huella": huella}
        return pk

    def cuenta_del_hogar(self, hogar_id, cuenta_id):
        return (hogar_id, cuenta_id) in self.cuentas

    def huellas_existentes(self, cuenta_id, huellas):
        return {
            m["huella"] for m in self.movimientos.values() if m["cuenta"] == cuenta_id and m["huella"] in set(huellas)
        }

    def candidatos(self, cuenta_id, desde, hasta):
        return [
            Candidato(pk, m["fecha"], m["importe"])
            for pk, m in self.movimientos.items()
            if m["cuenta"] == cuenta_id and not m["huella"] and desde <= m["fecha"] <= hasta
        ]

    def apuntar(self, *, hogar_id, actor, cuenta_id, filas):
        ids = []
        for f in filas:
            ids.append(self.nuevo(cuenta_id, f.fecha, f.importe, f.huella))
            self.movimientos[ids[-1]]["creado_por"] = actor.usuario_id
        return ids

    def conciliar(self, *, hogar_id, actor, huellas):
        hechos = {pk for pk in huellas if pk in self.movimientos and not self.movimientos[pk]["huella"]}
        for pk in hechos:
            self.movimientos[pk]["huella"] = huellas[pk]
        return hechos

    def eliminar(self, *, hogar_id, actor, ids):
        for pk in ids:
            self.movimientos.pop(pk, None)

    def desconciliar(self, *, hogar_id, actor, ids):
        for pk in ids:
            if pk in self.movimientos:
                self.movimientos[pk]["huella"] = ""
