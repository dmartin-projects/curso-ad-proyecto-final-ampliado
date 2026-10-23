"""Solo E2E (módulo 92, ejercicio 1): activa el MFA de una cuenta con un secreto TOTP conocido, para que Playwright
calcule sus códigos (e2e/ayuda.ts: SECRETO_SOPORTE). Lo llama preparar_e2e."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from usuarios.domain.bo.segundo_factor import SegundoFactor
from usuarios.infrastructure.database.repositories.segundo_factor_command_repository_orm import (
    SegundoFactorCommandRepositoryORM,
)
from usuarios.models import Usuario

SECRETO_E2E = "JBSWY3DPEHPK3PXP"  # público a propósito: solo existe en la base de datos de los E2E


class Command(BaseCommand):
    help = "Activa el MFA de una cuenta con un secreto conocido (solo con config.settings.e2e)"

    def add_arguments(self, parser):
        parser.add_argument("email")

    def handle(self, *args, email, **options):
        if settings.ROOT_URLCONF != "config.urls_e2e":
            raise CommandError("Solo con DJANGO_SETTINGS_MODULE=config.settings.e2e.")
        usuario = Usuario.objects.get(email=email)
        SegundoFactorCommandRepositoryORM().guardar(SegundoFactor(usuario.pk, SECRETO_E2E, activo=True))
