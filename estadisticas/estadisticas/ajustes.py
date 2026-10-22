# estadisticas/ajustes.py — configuración por variables de entorno (o un .env junto a pyproject.toml), con
# pydantic-settings (módulo 85). Solo la leen el composition root y la infraestructura (módulo 89).
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Ajustes(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Su PROPIA base de datos: el servicio nunca lee la de Django (módulo 85, §2)
    database_url: str = "postgresql+psycopg://gastos:gastos@localhost:5432/estadisticas"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_grupo: str = "estadisticas"  # el consumer group: Kafka guarda por él hasta dónde ha leído
    topic_movimientos: str = "gastos.movimientos"
    topic_membresias: str = "gastos.membresias"
    topic_dlq: str = "estadisticas.aparcados"  # ejercicio 3: mensajes que no se pueden aplicar
    # La misma clave con la que Django firma los JWT: el servicio los comprueba sin preguntar a Django
    jwt_signing_key: str


@lru_cache
def ajustes() -> Ajustes:
    return Ajustes()
