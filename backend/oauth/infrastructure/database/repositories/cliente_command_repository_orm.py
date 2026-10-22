# oauth/infrastructure/database/repositories/cliente_command_repository_orm.py — IClienteCommandRepository con las Application de django-oauth-toolkit (módulo 90)
from django.db import IntegrityError, transaction
from oauth2_provider.generators import generate_client_secret
from oauth2_provider.models import get_application_model

from oauth.domain.bo.cliente_nuevo import ClienteNuevo
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.domain.exceptions.cliente_ya_existe_exception import ClienteYaExisteException
from oauth.domain.repositories.i_cliente_command_repository import IClienteCommandRepository
from oauth.domain.vo.credenciales import Credenciales
from oauth.infrastructure.database.models.cliente_oauth_model import ClienteOAuth as ClienteOAuthModel

Application = get_application_model()


class ClienteCommandRepositoryORM(IClienteCommandRepository):
    def existe(self, client_id):
        return Application.objects.filter(client_id=client_id).exists()

    def crear(self, cliente: ClienteNuevo) -> Credenciales:
        secreto = generate_client_secret() if cliente.tipo.confidencial else ""
        aplicacion = Application(
            name=cliente.nombre,
            client_type=Application.CLIENT_CONFIDENTIAL if cliente.tipo.confidencial else Application.CLIENT_PUBLIC,
            authorization_grant_type=(
                Application.GRANT_AUTHORIZATION_CODE
                if cliente.tipo.con_usuario
                else Application.GRANT_CLIENT_CREDENTIALS
            ),
            redirect_uris=" ".join(cliente.redirect_uris),
            # El ID token, firmado con la clave privada del servidor (RS256): cualquiera lo verifica con la pública
            # (JWKS). HS256 usaría el client secret como clave: imposible en un public client.
            algorithm=Application.RS256_ALGORITHM if cliente.tipo.con_usuario else Application.NO_ALGORITHM,
            client_secret=secreto,
            hash_client_secret=True,  # en la base de datos, solo su hash (como una contraseña)
            skip_authorization=False,  # siempre la pantalla de consentimiento
        )
        if cliente.client_id is not None:
            aplicacion.client_id = cliente.client_id
        # Las validaciones de django-oauth-toolkit, además de las del dominio. La unicidad, no: la decide la base de
        # datos al guardar (dos registros a la vez pasarían los dos un SELECT previo)
        aplicacion.full_clean(validate_unique=False)
        try:
            with transaction.atomic():  # savepoint: el mismo client_id registrado a la vez
                aplicacion.save()
        except IntegrityError as e:
            raise ClienteYaExisteException() from e
        ClienteOAuthModel.objects.create(
            aplicacion=aplicacion, tipo=TipoCliente(cliente.tipo).value, scopes=sorted(cliente.scopes)
        )
        return Credenciales(client_id=aplicacion.client_id, client_secret=secreto or None)
