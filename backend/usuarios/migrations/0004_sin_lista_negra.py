# usuarios/migrations/0004_sin_lista_negra.py — módulo 92: la revocación de los refresh tokens es la de Sesion
#
# La lista negra de simplejwt (rest_framework_simplejwt.token_blacklist) sale de INSTALLED_APPS: Sesion recuerda el
# refresh vigente de cada sesión (su jti) y decide si se renueva. Sus dos tablas guardaban cada refresh token entero:
# se borran, con lo que tuvieran. (Sin la app instalada, Django ya no puede deshacer sus migraciones: se hace aquí.)
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0003_mfa_passkeys_sesiones")]

    operations = [
        migrations.RunSQL(
            [
                "DROP TABLE IF EXISTS token_blacklist_blacklistedtoken",
                "DROP TABLE IF EXISTS token_blacklist_outstandingtoken",
                "DELETE FROM django_migrations WHERE app = 'token_blacklist'",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
