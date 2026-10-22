# oauth/infrastructure/database/repositories/concesion_command_repository_orm.py — IConcesionCommandRepository con los tokens de django-oauth-toolkit (ejercicio 1)
from oauth2_provider.models import get_access_token_model, get_id_token_model, get_refresh_token_model

from oauth.domain.repositories.i_concesion_command_repository import IConcesionCommandRepository
from oauth.infrastructure.database.repositories.access_sueltos import access_sueltos

AccessToken, IDToken, RefreshToken = get_access_token_model(), get_id_token_model(), get_refresh_token_model()


class ConcesionCommandRepositoryORM(IConcesionCommandRepository):
    def _vivos(self, usuario_id, client_id):
        return RefreshToken.objects.filter(user_id=usuario_id, application__client_id=client_id, revoked__isnull=True)

    def tiene(self, usuario_id, client_id):
        sueltos = access_sueltos(user_id=usuario_id, application__client_id=client_id)
        return self._vivos(usuario_id, client_id).exists() or sueltos.exists()

    def revocar(self, usuario_id, client_id):
        sesiones = access_sueltos(user_id=usuario_id, application__client_id=client_id).count()
        for refresh in self._vivos(usuario_id, client_id).select_for_update():
            refresh.revoke()  # lo marca revocado y borra su access token
            sesiones += 1
        # Lo que quede (un access token sin refresh) y los ID tokens emitidos: fuera también
        AccessToken.objects.filter(user_id=usuario_id, application__client_id=client_id).delete()
        IDToken.objects.filter(user_id=usuario_id, application__client_id=client_id).delete()
        return sesiones
