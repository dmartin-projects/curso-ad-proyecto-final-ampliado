# asistente/application/agent/instrucciones.py — el system prompt, relleno con el contexto de la pregunta (módulo 96)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.prompts.sistema import SISTEMA
from asistente.domain.services.fechas_en_castellano import MESES, fecha_larga, mes_largo
from core.domain.vo.mes import Mes

VERSION = SISTEMA.version  # la que contesta: viaja en el log de cada pregunta


def instrucciones(contexto: ContextoPregunta) -> str:
    """Todo lo que depende del día sale del contexto (la hora de la sesión, en la zona del hogar), no del reloj del
    servidor ni del modelo: el mismo día, el mismo prompt, byte a byte (por eso los cassettes coinciden)."""
    hoy = contexto.hoy
    actual = Mes.de(hoy)
    anterior = actual.anterior()
    # "noviembre" el 29 de octubre de 2026 es noviembre de 2025: el ejemplo que más se equivoca, calculado
    siguiente_del_anio_pasado = Mes(actual.siguiente().anio - 1, actual.siguiente().numero)
    ejemplo = (
        f"«{MESES[anterior.numero - 1]}» es {anterior} y "
        f"«{MESES[siguiente_del_anio_pasado.numero - 1]}», {siguiente_del_anio_pasado}"
    )
    return SISTEMA.rellenar(
        hogar=contexto.hogar.nombre,
        hoy=fecha_larga(hoy),
        zona=contexto.hogar.zona_horaria,
        mes_actual=mes_largo(actual),
        dia=hoy.day,
        mes_anterior=mes_largo(anterior),
        ejemplo_meses=ejemplo,
        moneda=contexto.hogar.moneda,
    )
