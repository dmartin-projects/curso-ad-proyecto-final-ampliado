# oauth/infrastructure/database/repositories/aplicacion_conectada_query_service_orm.py — "Aplicaciones conectadas" (ejercicio 1 del módulo 90)
from django.db.models import Max, Min
from oauth2_provider.models import get_refresh_token_model

from oauth.domain.read_models.aplicacion_conectada import AplicacionConectada
from oauth.domain.repositories.i_aplicacion_conectada_query_service import IAplicacionConectadaQueryService
from oauth.infrastructure.database.repositories.access_sueltos import access_sueltos

RefreshToken = get_refresh_token_model()


class AplicacionConectadaQueryServiceORM(IAplicacionConectadaQueryService):
    def listar(self, usuario_id: int) -> list[AplicacionConectada]:
        """Las aplicaciones con algún refresh token vivo de este usuario (o un access token vigente sin él: también
        puede usarlo), y los scopes que le ha dado."""
        vivos = RefreshToken.objects.filter(user_id=usuario_id, revoked__isnull=True)
        sueltos = access_sueltos(user_id=usuario_id)
        apps: dict[str, dict] = {}
        for consulta in (vivos, sueltos):
            filas = consulta.values("application__client_id", "application__name").annotate(
                desde=Min("created"), ultimo_uso=Max("updated")
            )
            for f in filas:
                app = apps.setdefault(f["application__client_id"], f | {"scopes": set()})
                app["desde"] = min(app["desde"], f["desde"])
                app["ultimo_uso"] = max(app["ultimo_uso"], f["ultimo_uso"])
        for client_id, scope in [
            *vivos.filter(access_token__isnull=False).values_list("application__client_id", "access_token__scope"),
            *sueltos.values_list("application__client_id", "scope"),
        ]:
            apps[client_id]["scopes"].update(scope.split())
        return [
            AplicacionConectada(
                client_id=client_id,
                nombre=app["application__name"],
                scopes=tuple(sorted(app["scopes"])),
                desde=app["desde"],
                ultimo_uso=app["ultimo_uso"],
            )
            for client_id, app in sorted(apps.items(), key=lambda par: par[1]["ultimo_uso"], reverse=True)
        ]
