# asistente/infrastructure/database/mappers/mensaje_mapper.py — un Mensaje del dominio, como JSON (módulo 97)
"""El historial se guarda en el formato del DOMINIO, no en el de un proveedor: cambiar de Groq a Claude (módulo 106) no
obliga a migrar las conversaciones; cada adapter traduce al enviar."""

from typing import Any

from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.resultado_tool import ResultadoTool


def mensaje_a_json(m: Mensaje) -> dict[str, Any]:
    datos: dict[str, Any] = {"rol": str(m.rol)}
    if m.texto:
        datos["texto"] = m.texto
    if m.llamadas:
        datos["llamadas"] = [{"id": ll.id, "nombre": ll.nombre, "argumentos": ll.argumentos} for ll in m.llamadas]
    if m.resultados:
        datos["resultados"] = [
            {"llamada_id": r.llamada_id, "nombre": r.nombre, "contenido": r.contenido, "es_error": r.es_error}
            for r in m.resultados
        ]
    return datos


def mensaje_de_json(datos: dict[str, Any]) -> Mensaje:
    return Mensaje(
        RolMensaje(datos["rol"]),
        texto=datos.get("texto", ""),
        llamadas=tuple(LlamadaTool(**ll) for ll in datos.get("llamadas", ())),
        resultados=tuple(ResultadoTool(**r) for r in datos.get("resultados", ())),
    )
