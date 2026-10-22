# estadisticas/infrastructure/database/conexion.py — ¿responde PostgreSQL? (módulos 85 y 89)
from sqlalchemy import text
from sqlalchemy.orm import Session


def comprobar_conexion(s: Session) -> None:
    s.execute(text("SELECT 1"))
