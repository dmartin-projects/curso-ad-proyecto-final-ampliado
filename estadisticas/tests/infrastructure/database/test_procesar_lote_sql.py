"""ProcesarLoteUseCase con PostgreSQL de verdad (módulo 89): lo que un fake no puede comprobar.

En PostgreSQL, un error dentro de una transacción la deja ROTA: todo lo que venga detrás falla hasta el ROLLBACK.
Por eso, al repetir un lote "con cuidado", cada mensaje va en su savepoint. Los fakes no tienen transacciones
rotas; este test sí. Sin Kafka: el topic de aparcados se cambia por el fake en el composition root.
"""

from decimal import Decimal

from sqlalchemy import select

from estadisticas.infrastructure import container
from estadisticas.infrastructure.database.models.movimiento_model import MovimientoModel
from estadisticas.infrastructure.database.sesiones import sesion
from tests.fakes import mundo
from tests.fakes.aparcados_fake import AparcadosFake


def test_lo_que_postgresql_rechaza_se_aparca_y_el_resto_del_lote_se_aplica(monkeypatch):
    aparcados = AparcadosFake()
    monkeypatch.setattr(container, "AparcadosKafka", lambda *_: aparcados)
    mensajes = [
        mundo.movimiento(1, offset=0),
        mundo.movimiento(2, importe="99999999999.00", offset=1),  # Numeric(12, 2): PostgreSQL dice que no cabe
        mundo.movimiento(3, offset=2),
    ]
    container.procesar_lote().ejecutar(mundo.lote(mensajes))
    with sesion() as s:
        assert dict(s.execute(select(MovimientoModel.id, MovimientoModel.importe)).all()) == {
            1: Decimal("-10.00"),
            3: Decimal("-10.00"),
        }
    assert [(m.offset, type(e).__name__) for m, e in aparcados.guardados] == [(1, "DataError")]
