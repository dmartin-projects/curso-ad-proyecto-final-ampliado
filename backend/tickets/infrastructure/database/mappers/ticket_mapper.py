# tickets/infrastructure/database/mappers/ticket_mapper.py — BO ↔ fila (y los datos de la IA ↔ JSON) (módulo 88)
import json
from datetime import date
from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder

from tickets.domain.bo.ticket import Ticket
from tickets.domain.vo.datos_ticket import DatosTicket
from tickets.domain.vo.linea import Linea
from tickets.infrastructure.database.models.ticket_model import Ticket as TicketModel


# ── Los datos de la IA, como JSON (el mismo que guardaba el módulo 74: lo lee el frontend y las notificaciones) ──
def datos_a_json(d: DatosTicket | None) -> dict:
    if d is None:
        return {}
    datos = {
        "comercio": d.comercio,
        "nif": d.nif,
        "fecha": d.fecha,
        "total": d.total,
        "moneda": d.moneda,
        "categoria": d.categoria,
        "lineas": [
            {"descripcion": li.descripcion, "cantidad": li.cantidad, "precio_unitario": li.precio_unitario}
            for li in d.lineas
        ],
        "confianza": d.confianza,
    }
    return json.loads(json.dumps(datos, cls=DjangoJSONEncoder))  # Decimal y date → texto, como el JSONField


def datos_de_json(j: dict) -> DatosTicket | None:
    if not j:
        return None
    return DatosTicket(
        comercio=j["comercio"],
        nif=j.get("nif", ""),
        fecha=date.fromisoformat(j["fecha"]) if j.get("fecha") else None,
        total=Decimal(j["total"]) if j.get("total") is not None else None,
        moneda=j.get("moneda", "EUR"),
        categoria=j.get("categoria", ""),
        lineas=tuple(
            Linea(li["descripcion"], Decimal(li["cantidad"]), Decimal(li["precio_unitario"])) for li in j["lineas"]
        ),
        confianza=j["confianza"],
    )


def ticket_a_bo(fila: TicketModel, lineas: list | None = None) -> Ticket:
    return Ticket(
        id=fila.pk,
        hogar_id=fila.hogar_id,
        cuenta_id=fila.cuenta_id,
        subido_por_id=fila.subido_por_id,
        archivo=fila.archivo.name,
        nombre_original=fila.nombre_original,
        tipo_archivo=fila.tipo,
        huella_archivo=fila.huella_archivo,
        estado=fila.estado,
        intentos=fila.intentos,
        texto_ocr=fila.texto_ocr,
        datos=datos_de_json(fila.datos_ia),
        confianza=fila.confianza,
        error=fila.error,
        procesado_en=fila.procesado_en,
        movimiento_id=fila.movimiento_id,
        lineas=[Linea(li.descripcion, li.cantidad, li.precio_unitario) for li in (lineas or [])],
    )
