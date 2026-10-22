"""El BO Movimiento (módulo 87): sus reglas se cumplen siempre, sin base de datos."""

from datetime import date

import pytest

from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.domain.bo.movimiento import Movimiento
from finanzas.domain.enums.origen import Origen
from finanzas.domain.exceptions.concepto_vacio_exception import ConceptoVacioException
from finanzas.domain.exceptions.fecha_futura_exception import FechaFuturaException
from finanzas.domain.exceptions.importe_cero_exception import ImporteCeroException
from finanzas.domain.exceptions.movimiento_ya_conciliado_exception import MovimientoYaConciliadoException

HOY = date(2026, 10, 15)


def mov(**cambios) -> Movimiento:
    datos = {"hogar_id": 1, "cuenta_id": 10, "fecha": HOY, "importe": Dinero("-12.5"), "concepto": "Pan"}
    return Movimiento(**datos | cambios)


def test_invariantes():
    with pytest.raises(ImporteCeroException) as error:
        mov(importe=Dinero("0.001"))  # se redondea a 0,00: también es cero
    assert error.value.campo == "importe"  # la API lo enseñará en errors.importe
    with pytest.raises(ConceptoVacioException):
        mov(concepto="   ")


def test_etiquetas_normalizadas_y_origen():
    m = mov(etiquetas=[" Casa", "casa", "Mes", ""], origen="ticket")
    assert m.etiquetas == ["casa", "mes"] and m.origen is Origen.TICKET
    assert m.es_gasto and m.mes == Mes(2026, 10)


def test_registrar_no_admite_fechas_futuras_pero_un_extracto_si():
    with pytest.raises(FechaFuturaException):
        Movimiento.registrar(
            hoy=HOY, hogar_id=1, cuenta_id=1, fecha=date(2026, 10, 16), importe=Dinero(-1), concepto="x"
        )
    assert mov(fecha=date(2026, 10, 16), origen=Origen.EXTRACTO).fecha == date(2026, 10, 16)  # el banco manda


def test_modificar_es_todo_o_nada_y_devuelve_los_meses():
    m = mov()
    assert m.modificar(hoy=HOY, fecha=date(2026, 9, 30), concepto="Pan y leche") == {Mes(2026, 10), Mes(2026, 9)}
    assert (m.fecha, m.concepto) == (date(2026, 9, 30), "Pan y leche")
    with pytest.raises(ImporteCeroException):
        m.modificar(hoy=HOY, concepto="Otro", importe=Dinero(0))
    assert m.concepto == "Pan y leche"  # el concepto válido NO se ha aplicado: ni uno ni otro
    with pytest.raises(TypeError):
        m.modificar(hoy=HOY, hogar_id=2)  # el hogar no se cambia


def test_recategorizar_es_revisar():
    m = mov(revisado=False)
    m.modificar(hoy=HOY, **Movimiento.cambios_al_recategorizar(4))
    assert (m.categoria_id, m.revisado) == (4, True)


def test_auditoria_con_los_nombres_de_siempre():
    m = mov(id=3)
    assert str(m) == "2026-10-15 Pan -12.50"  # como el __str__ del modelo de Django
    assert m.datos_auditables()["importe"] == Dinero("-12.50") and "cuenta" in m.datos_auditables()


def test_conciliar_una_sola_fila_del_banco_y_propuestas():  # módulo 88
    m = mov(origen=Origen.TICKET, revisado=False)
    assert m.es_propuesta and not m.conciliado
    m.conciliar("h1")
    m.conciliar("h1")  # la misma fila otra vez: nada que hacer
    with pytest.raises(MovimientoYaConciliadoException):
        m.conciliar("h2")  # otra fila del banco: no, ya tiene la suya
    m.desconciliar()
    assert m.huella == "" and not mov(revisado=False).es_propuesta  # uno manual nunca es una "propuesta"
