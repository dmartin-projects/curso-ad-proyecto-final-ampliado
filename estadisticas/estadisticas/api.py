"""La API del servicio de estadísticas (módulo 85): `uvicorn estadisticas.api:app`.

Solo lectura, sobre su propia base de datos. Autenticación con el MISMO JWT que emite Django: el servicio
comprueba la firma con la clave compartida y saca el usuario del token, sin llamar a Django.
"""

from collections.abc import Iterator
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import Integer, case, cast, extract, func, select, text
from sqlalchemy.orm import Session

from . import telemetria
from .ajustes import ajustes
from .bd import Membresia, Movimiento, Progreso, sesion

if telemetria.configurar("estadisticas-api"):
    from .retraso import registrar_metrica

    registrar_metrica()  # ejercicio 2: el retraso del consumidor, medido desde la API
app = FastAPI(title="Estadísticas de Gastos", version="1.0", docs_url="/estadisticas/docs",
              openapi_url="/estadisticas/openapi.json")  # fmt: skip
telemetria.instrumentar_api(app)
PREFIJO = "/estadisticas/v1"  # el mismo en desarrollo y detrás de Caddy: sin reescribir rutas


# ── Dependencias ──
def bd() -> Iterator[Session]:
    with sesion() as s:
        yield s


Bd = Annotated[Session, Depends(bd)]
bearer = HTTPBearer(auto_error=False)


def usuario_actual(credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> int:
    no_autenticado = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Credenciales no válidas", {"WWW-Authenticate": "Bearer"}
    )
    if credenciales is None:
        raise no_autenticado
    try:
        datos = jwt.decode(
            credenciales.credentials,
            ajustes().jwt_signing_key,
            algorithms=["HS256"],  # SIEMPRE la lista explícita: nunca aceptar el algoritmo que diga el token
            options={"require": ["exp", "user_id", "token_type"]},
        )
    except jwt.InvalidTokenError as e:  # firma mala, caducado, mal formado…
        raise no_autenticado from e
    if datos["token_type"] != "access":  # un refresh token no sirve para llamar a la API
        raise no_autenticado
    return int(datos["user_id"])


def hogar_permitido(hogar_id: int, usuario: Annotated[int, Depends(usuario_actual)], s: Bd) -> int:
    es_miembro = s.scalar(select(func.count()).where(Membresia.hogar_id == hogar_id, Membresia.usuario_id == usuario))
    if not es_miembro:  # 404 y no 403: no revelar que el hogar existe (como en Django, módulo 36)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
    return hogar_id


Hogar = Annotated[int, Depends(hogar_permitido)]


# ── Respuestas ──
class Mes(BaseModel):
    mes: str  # "2026-10"
    gastos: Decimal
    ingresos: Decimal
    ahorro: Decimal


class Tendencia(BaseModel):
    hogar_id: int
    # Cuándo se publicó el último cambio que ya está aplicado. El servicio va unos instantes por detrás de
    # Django (consistencia eventual): la interfaz puede decir "datos de hace X segundos"
    ultimo_evento: datetime | None
    meses: list[Mes]


class DiaSemana(BaseModel):
    dia: int  # 1 = lunes … 7 = domingo (ISO)
    nombre: str
    gasto_medio: Decimal


class DiasSemana(BaseModel):
    hogar_id: int
    ultimo_evento: datetime | None
    desde: date
    hasta: date  # el último día contado (el mes en curso, solo hasta hoy)
    dias: list[DiaSemana]


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _mes(texto: str | None) -> date:
    if texto is None:
        return date.today().replace(day=1)
    try:
        return datetime.strptime(texto, "%Y-%m").date()
    except ValueError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "hasta: formato AAAA-MM") from e


def _restar_meses(d: date, n: int) -> date:
    total = d.year * 12 + d.month - 1 - n
    return date(total // 12, total % 12 + 1, 1)


def _ultimo_evento(s: Session) -> datetime | None:
    return s.scalar(select(func.max(Progreso.marca)))


# ── Endpoints ──
@app.get(f"{PREFIJO}/salud", include_in_schema=False)
def salud(s: Bd) -> dict:
    s.execute(text("SELECT 1"))
    return {"bd": "ok", "ultimo_evento": _ultimo_evento(s)}


@app.get(f"{PREFIJO}/hogares/{{hogar_id}}/tendencia", response_model=Tendencia)
def tendencia(
    hogar_id: Hogar, s: Bd, meses: Annotated[int, Query(ge=1, le=36)] = 12, hasta: str | None = None
) -> Tendencia:
    """Gastos, ingresos y ahorro de los últimos `meses` (incluido el de `hasta`, por defecto el actual)."""
    ultimo = _mes(hasta)
    primero = _restar_meses(ultimo, meses - 1)
    mes = func.date_trunc("month", Movimiento.fecha).label("mes")
    filas = s.execute(
        select(
            mes,
            func.coalesce(func.sum(case((Movimiento.importe < 0, -Movimiento.importe), else_=0)), 0),
            func.coalesce(func.sum(case((Movimiento.importe > 0, Movimiento.importe), else_=0)), 0),
        )
        .where(
            Movimiento.hogar_id == hogar_id, Movimiento.fecha >= primero, Movimiento.fecha < _restar_meses(ultimo, -1)
        )
        .group_by(mes)
    ).all()
    por_mes = {f.mes.date(): (Decimal(f[1]), Decimal(f[2])) for f in filas}
    resultado = []
    for i in range(meses):  # todos los meses, también los que no tienen movimientos (para el gráfico)
        m = _restar_meses(ultimo, meses - 1 - i)
        gastos, ingresos = por_mes.get(m, (Decimal("0"), Decimal("0")))
        resultado.append(Mes(mes=f"{m:%Y-%m}", gastos=gastos, ingresos=ingresos, ahorro=ingresos - gastos))
    return Tendencia(hogar_id=hogar_id, ultimo_evento=_ultimo_evento(s), meses=resultado)


@app.get(f"{PREFIJO}/hogares/{{hogar_id}}/dias-semana", response_model=DiasSemana)
def dias_semana(
    hogar_id: Hogar, s: Bd, meses: Annotated[int, Query(ge=1, le=36)] = 6, hasta: str | None = None
) -> DiasSemana:
    """Cuánto se gasta de media cada día de la semana: total de ese día ÷ cuántos hubo en el periodo."""
    # Un mes futuro cuenta como el actual: el periodo no puede acabar después de hoy (si no, empezaría después
    # de terminar y las medias no tendrían sentido)
    ultimo = min(_mes(hasta), date.today().replace(day=1))
    fin = _restar_meses(ultimo, -1)  # primer día del mes siguiente (excluido)
    inicio = _restar_meses(fin, meses)
    # El mes en curso, solo hasta hoy: si no, los días que aún no han llegado bajarían la media
    fin = min(fin, date.today() + timedelta(days=1))
    dia = cast(extract("isodow", Movimiento.fecha), Integer).label("dia")
    totales = dict(
        s.execute(
            select(dia, func.sum(-Movimiento.importe))
            .where(Movimiento.hogar_id == hogar_id, Movimiento.importe < 0)
            .where(Movimiento.fecha >= inicio, Movimiento.fecha < fin)
            .group_by(dia)
        ).all()
    )
    dias_totales = (fin - inicio).days
    cuantos = {
        d: dias_totales // 7 + (1 if (d - inicio.isoweekday()) % 7 < dias_totales % 7 else 0) for d in range(1, 8)
    }
    dias = [
        DiaSemana(
            dia=d, nombre=DIAS[d - 1], gasto_medio=(Decimal(totales.get(d, 0)) / cuantos[d]).quantize(Decimal("0.01"))
        )
        for d in range(1, 8)
    ]
    return DiasSemana(
        hogar_id=hogar_id, ultimo_evento=_ultimo_evento(s), desde=inicio, hasta=fin - timedelta(days=1), dias=dias
    )


# ── Ejercicio 4: un dato que el servicio ignoraba, recuperado reconstruyendo desde Kafka ──
class MesSinRevisar(BaseModel):
    mes: str
    movimientos: int
    gastos: Decimal


class SinRevisar(BaseModel):
    hogar_id: int
    ultimo_evento: datetime | None
    meses: list[MesSinRevisar]


@app.get(f"{PREFIJO}/hogares/{{hogar_id}}/sin-revisar", response_model=SinRevisar)
def sin_revisar(
    hogar_id: Hogar, s: Bd, meses: Annotated[int, Query(ge=1, le=36)] = 6, hasta: str | None = None
) -> SinRevisar:
    """Cuántos movimientos (y cuánto gasto) quedan por revisar, mes a mes: lo que trajo la IA o el banco."""
    ultimo = _mes(hasta)
    primero = _restar_meses(ultimo, meses - 1)
    mes = func.date_trunc("month", Movimiento.fecha).label("mes")
    filas = s.execute(
        select(
            mes,
            func.count(),
            func.coalesce(func.sum(case((Movimiento.importe < 0, -Movimiento.importe), else_=0)), 0),
        )
        .where(Movimiento.hogar_id == hogar_id, Movimiento.revisado.is_(False))
        .where(Movimiento.fecha >= primero, Movimiento.fecha < _restar_meses(ultimo, -1))
        .group_by(mes)
    ).all()
    por_mes = {f.mes.date(): (f[1], Decimal(f[2])) for f in filas}
    resultado = []
    for i in range(meses):
        m = _restar_meses(ultimo, meses - 1 - i)
        n, gastos = por_mes.get(m, (0, Decimal("0")))
        resultado.append(MesSinRevisar(mes=f"{m:%Y-%m}", movimientos=n, gastos=gastos))
    return SinRevisar(hogar_id=hogar_id, ultimo_evento=_ultimo_evento(s), meses=resultado)
