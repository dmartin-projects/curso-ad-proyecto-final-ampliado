# estadisticas/infrastructure/database/metadata.py — todas las tablas del servicio (módulo 89)
#
# La puerta de entrada de los modelos, como `<app>/models.py` en Django: un modelo solo entra en
# `Base.metadata` cuando se importa su archivo. Lo leen Alembic (migraciones/env.py) y el test de las migraciones.
from estadisticas.infrastructure.database.models.base import Base
from estadisticas.infrastructure.database.models.membresia_model import MembresiaModel
from estadisticas.infrastructure.database.models.movimiento_model import MovimientoModel
from estadisticas.infrastructure.database.models.progreso_model import ProgresoModel

metadata = Base.metadata

__all__ = ["metadata", "MembresiaModel", "MovimientoModel", "ProgresoModel"]
