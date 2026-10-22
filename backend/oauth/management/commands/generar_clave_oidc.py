# oauth/management/commands/generar_clave_oidc.py — la clave privada con la que se firman los ID tokens (módulo 90)
from django.core.management import BaseCommand

from oauth.infrastructure.crypto.claves import nueva_clave_pem


class Command(BaseCommand):
    help = "Escribe una línea OIDC_RSA_PRIVATE_KEY=… para el .env (desarrollo) o para los secretos (SOPS)."

    def handle(self, **opciones):
        # En una sola línea, con \n: así cabe en un .env y en SOPS; los ajustes la leen con env.str(multiline=True)
        self.stdout.write('OIDC_RSA_PRIVATE_KEY="' + nueva_clave_pem().strip().replace("\n", "\\n") + '"')
