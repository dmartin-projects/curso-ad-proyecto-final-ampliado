"""Una clave para cifrar los secretos TOTP (módulo 92): uv run python manage.py generar_clave_mfa >> .env"""

from cryptography.fernet import Fernet
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Genera una clave Fernet para MFA_CLAVES (módulo 92)"

    def handle(self, *args, **options):
        self.stdout.write(f"MFA_CLAVES={Fernet.generate_key().decode()}")
