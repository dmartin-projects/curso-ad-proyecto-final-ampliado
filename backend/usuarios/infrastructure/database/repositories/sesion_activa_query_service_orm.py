# usuarios/infrastructure/database/repositories/sesion_activa_query_service_orm.py — «Sesiones» (módulo 92)
from usuarios.domain.read_models.sesion_activa import SesionActiva
from usuarios.domain.repositories.i_sesion_activa_query_service import ISesionActivaQueryService
from usuarios.infrastructure.database.services.sesiones_orm import vigentes


class SesionActivaQueryServiceORM(ISesionActivaQueryService):
    def de_usuario(self, usuario_id: int, sid_actual: str | None) -> list[SesionActiva]:
        filas = vigentes().filter(usuario_id=usuario_id).order_by("-ultimo_uso")
        return [
            SesionActiva(str(s.sid), s.canal, s.descripcion, s.ip, s.creada, s.ultimo_uso, tuple(s.factores),
                         str(s.sid) == sid_actual)
            for s in filas
        ]  # fmt: skip
