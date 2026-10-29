"""Módulo 93: PeticionLLM, lo que viaja en una llamada, comprobado al construirse."""

import pytest

from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM

HOLA = (Mensaje.usuario("hola"),)


def test_por_defecto_sin_tools_ni_opciones():
    p = PeticionLLM(sistema="Responde breve.", mensajes=HOLA)
    assert (p.tools, p.usar_tools, p.esquema, p.temperatura, p.esfuerzo, p.max_tokens) == (
        (),
        True,
        None,
        None,
        None,
        None,
    )


@pytest.mark.parametrize(
    "cambios, error",
    [
        ({"mensajes": ()}, "al menos un mensaje"),
        ({"temperatura": 2.5}, "de 0 a 2"),
        ({"temperatura": -0.1}, "de 0 a 2"),
        ({"max_tokens": 0}, "positivo"),
    ],
)
def test_reglas(cambios, error):
    with pytest.raises(ValueError, match=error):
        PeticionLLM(**{"sistema": "", "mensajes": HOLA} | cambios)
