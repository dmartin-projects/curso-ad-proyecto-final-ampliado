"""Aplicar un evento de Kafka a la base de datos del servicio (módulo 85). Sin Kafka: fácil de probar.

IDEMPOTENTE: cada mensaje lleva en la cabecera "version" el id del evento en el outbox de Django, que crece
con cada cambio. Solo se aplica si es más nuevo que lo que ya hay. Así da igual recibir un mensaje dos
veces (el relay y el consumidor garantizan "al menos una vez") o volver a leer el topic desde el principio.
"""

import json
import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .ajustes import ajustes
from .bd import Membresia, Movimiento

logger = logging.getLogger(__name__)
ESQUEMAS = {"1"}  # versiones del formato que este servicio entiende


class EsquemaDesconocido(Exception):
    """Un mensaje con un formato que este servicio todavía no entiende (ver el módulo 85, §4)."""


def aplicar(sesion: Session, topic: str, clave: str, valor: bytes | None, cabeceras: dict[str, str]) -> str:
    """Aplica un mensaje. Devuelve lo que ha hecho: "guardado", "borrado" o "ignorado"."""
    if cabeceras.get("esquema") not in ESQUEMAS:
        raise EsquemaDesconocido(f"{topic} {clave}: esquema {cabeceras.get('esquema')!r}")
    version = int(cabeceras["version"])
    datos = None if valor is None else json.loads(valor)
    a = ajustes()
    if topic == a.topic_movimientos:
        return _movimiento(sesion, int(clave), datos, version)
    if topic == a.topic_membresias:
        hogar_id, usuario_id = (int(x) for x in clave.split(":"))
        return _membresia(sesion, hogar_id, usuario_id, datos, version)
    logger.warning("Topic desconocido: %s", topic)
    return "ignorado"


def _movimiento(sesion: Session, pk: int, datos: dict | None, version: int) -> str:
    if datos is None:  # tombstone: el movimiento ya no existe
        r = sesion.execute(delete(Movimiento).where(Movimiento.id == pk, Movimiento.version < version))
        return "borrado" if r.rowcount else "ignorado"
    fila = {
        "id": pk,
        "hogar_id": datos["hogar_id"],
        "cuenta_id": datos["cuenta_id"],
        "fecha": date.fromisoformat(datos["fecha"]),
        "importe": Decimal(datos["importe"]),
        "categoria_id": datos["categoria_id"],
        "comercio_id": datos["comercio_id"],
        "origen": datos["origen"],
        "version": version,
    }
    # INSERT … ON CONFLICT DO UPDATE … WHERE: un "upsert" que solo pisa la fila si el evento es más nuevo.
    # Una sola sentencia: sin "leer y luego escribir", que con dos consumidores sería una condición de carrera.
    sentencia = insert(Movimiento).values(fila)
    sentencia = sentencia.on_conflict_do_update(
        index_elements=[Movimiento.id],
        set_={k: getattr(sentencia.excluded, k) for k in fila if k != "id"},
        where=Movimiento.version < sentencia.excluded.version,
    ).returning(Movimiento.id)
    # RETURNING y no rowcount: en esta sentencia SQLAlchemy devuelve rowcount = -1 ("no lo sé"), que es
    # verdadero en Python: con rowcount, todo contaría como "guardado", también lo que el WHERE ha descartado
    return "guardado" if sesion.execute(sentencia).first() else "ignorado"


def _membresia(sesion: Session, hogar_id: int, usuario_id: int, datos: dict | None, version: int) -> str:
    clave = (Membresia.hogar_id == hogar_id) & (Membresia.usuario_id == usuario_id)
    if datos is None:
        r = sesion.execute(delete(Membresia).where(clave, Membresia.version < version))
        return "borrado" if r.rowcount else "ignorado"
    sentencia = insert(Membresia).values(hogar_id=hogar_id, usuario_id=usuario_id, rol=datos["rol"], version=version)
    sentencia = sentencia.on_conflict_do_update(
        index_elements=[Membresia.hogar_id, Membresia.usuario_id],
        set_={"rol": sentencia.excluded.rol, "version": sentencia.excluded.version},
        where=Membresia.version < sentencia.excluded.version,
    ).returning(Membresia.hogar_id)
    return "guardado" if sesion.execute(sentencia).first() else "ignorado"
