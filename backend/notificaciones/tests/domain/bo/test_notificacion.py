"""La notificación (módulo 88), sin base de datos."""

from datetime import date

from notificaciones.domain.bo.notificacion import Notificacion


def test_titulo_recortado_y_datos_como_texto():
    n = Notificacion(usuario_id=1, tipo="informe_listo", titulo="x" * 200, datos={"mes": date(2026, 10, 1), "n": 3})
    assert len(n.titulo) == 150 and n.datos == {"mes": "2026-10-01", "n": "3"} and n.tipo == "informe_listo"
