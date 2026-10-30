"""Módulo 97: lo común a los tests de la API del chat."""

import pytest

from asistente.infrastructure import container
from asistente.tests.fakes.llm_fake import LLMFake


@pytest.fixture
def llm(monkeypatch, settings):
    """El modelo de la pregunta y el auxiliar (el título), con guion: lo que el test meta en .guion."""
    settings.ASISTENTE_API_KEY = "fake"
    principal, auxiliar = LLMFake([]), LLMFake([LLMFake.responder("Gasto de septiembre")])
    monkeypatch.setattr(container, "llm", lambda modelo=None: principal)
    monkeypatch.setattr(container, "llm_auxiliar", lambda: auxiliar)
    return principal
