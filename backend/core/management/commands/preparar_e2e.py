from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import BaseCommand, CommandError, call_command

from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Deja la BD de pruebas E2E en un estado conocido (solo con config.settings.e2e)."

    def handle(self, *args, **opciones):
        if settings.ROOT_URLCONF != "config.urls_e2e":
            raise CommandError("Solo con DJANGO_SETTINGS_MODULE=config.settings.e2e: borra todos los datos.")
        call_command("flush", interactive=False, verbosity=0)  # vacía las tablas; post_migrate recrea los grupos
        call_command("seed", movimientos=300, verbosity=0)  # demo@example.com / demo12345-demo
        soporte = Usuario.objects.create_user("soporte@example.com", "soporte12345", nombre="Soporte", is_staff=True)
        soporte.groups.add(Group.objects.get(name="Soporte"))
        # Módulo 92, ejercicio 1: el personal, con MFA (el secreto que usa e2e/soporte.spec.ts para calcular el código)
        call_command("mfa_e2e", "soporte@example.com", verbosity=0)
        # Módulo 92: una cuenta para cada prueba de e2e/mfa.spec.ts (activan el MFA, añaden passkeys, cierran sesiones)
        for nombre in ("mfa", "passkey", "sesiones", "stepup"):
            Usuario.objects.create_user(f"{nombre}@example.com", f"{nombre}-clave-e2e", nombre=nombre.capitalize())
        # Módulo 90: el CLI, para la prueba de la pantalla de consentimiento (e2e/oauth.spec.ts)
        call_command(
            "crear_cliente_oauth", "Gastos CLI", tipo="nativa", client_id="gastos-cli",
            scopes="openid email gastos:leer gastos:escribir", redirect_uris=["http://127.0.0.1/callback"], verbosity=0,
        )  # fmt: skip
        call_command("indexar_ayuda", verbosity=0)  # módulo 100: la ayuda del asistente (por texto: sin embeddings)
        self.stdout.write(self.style.SUCCESS("BD E2E preparada"))
