# oauth/management/commands/crear_cliente_oauth.py — registrar una aplicación cliente (módulo 90)
from django.core.management import BaseCommand, CommandError

from core.domain.exceptions.dominio_exception import DominioException
from oauth.application.registrar_cliente_use_case.dtos.registrar_cliente_input_dto import RegistrarClienteInputDTO
from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.infrastructure import container


class Command(BaseCommand):
    help = "Registra una aplicación que podrá pedir tokens a Gastos (authorization code + PKCE, o client credentials)."

    def add_arguments(self, parser):
        parser.add_argument("nombre", help="el que verá el usuario en la pantalla de consentimiento")
        parser.add_argument("--tipo", choices=[t.value for t in TipoCliente], required=True)
        parser.add_argument("--scopes", required=True, help='separados por espacios: "openid email gastos:leer"')
        parser.add_argument("--redirect-uri", action="append", default=[], dest="redirect_uris")
        parser.add_argument("--client-id", help="fijo (una app nativa conocida, como gastos-cli); si no, aleatorio")

    def handle(self, nombre, tipo, scopes, redirect_uris, client_id, **opciones):
        entrada = RegistrarClienteInputDTO(
            nombre, TipoCliente(tipo), frozenset(scopes.split()), tuple(redirect_uris), client_id
        )
        try:
            credenciales = container.registrar_cliente().ejecutar(entrada)
        except DominioException as e:
            raise CommandError(e.mensaje) from e
        self.stdout.write(f"client_id: {credenciales.client_id}")
        if credenciales.client_secret:
            self.stdout.write(f"client_secret: {credenciales.client_secret}")
            self.stdout.write(self.style.WARNING("Guárdalo ahora: solo se guarda su hash y no se puede volver a ver."))
