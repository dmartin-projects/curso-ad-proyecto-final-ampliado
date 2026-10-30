"""Módulo 96, ejercicio 2: manage.py ver_prompt, el prompt que vería el modelo, sin llamarlo."""

from io import StringIO

from django.core.management import call_command


def test_el_prompt_de_otro_dia(casa):
    ana, hogar = casa
    salida = StringIO()
    call_command("ver_prompt", "--ahora=2027-01-15T12:00:00+00:00", email=ana.email, hogar=hogar.pk, stdout=salida)
    texto = salida.getvalue()
    assert "Hoy es viernes, 15 de enero de 2027, en Europe/Madrid." in texto
    assert "«diciembre» es 2026-12 y «febrero», 2026-02" in texto
    assert "[sistema 2026-10-29.1 · huella" in texto
