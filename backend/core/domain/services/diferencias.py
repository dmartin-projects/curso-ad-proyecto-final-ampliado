# core/domain/services/diferencias.py — la regla de qué se apunta en la auditoría (módulos 15, 17 y 87)
NUNCA = {"password"}  # ni siquiera el hash: la auditoría la lee el personal de soporte


def diferencias(antes: dict, despues: dict) -> dict[str, list[str]]:
    """{campo: [antes, después]} de los campos de `antes` que han cambiado, como texto."""
    return {
        campo: [str(valor), str(despues[campo])]
        for campo, valor in antes.items()
        if campo in despues and campo not in NUNCA and valor != despues[campo]
    }
