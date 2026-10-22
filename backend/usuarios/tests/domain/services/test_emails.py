"""Cómo se identifica a una persona (módulo 88), sin base de datos."""

import pytest

from usuarios.domain.exceptions.email_no_valido_exception import EmailNoValidoException
from usuarios.domain.services.emails import normalizar_email


def test_el_email_entero_en_minusculas():
    assert normalizar_email("  Ana@Example.COM ") == "ana@example.com"  # normalize_email de Django: solo el dominio
    for malo in ("", "ana", "@", "ana@"[:-1]):
        with pytest.raises(EmailNoValidoException):
            normalizar_email(malo)
