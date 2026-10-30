# asistente/application/prompts/versiones.py — las versiones publicadas de cada prompt, con su huella (módulos 96, 97 y 99)
#
# Cambiar el texto de un prompt es cambiar el comportamiento del asistente: lleva versión nueva, una línea aquí y los
# cassettes grabados de nuevo. El test de prompts comprueba que la huella del texto actual es la de su versión: un
# cambio "de una palabra" sin versión nueva no pasa el CI. Las antiguas se quedan: el log de una pregunta de hace un
# mes dice qué versión contestó.
PUBLICADAS: dict[tuple[str, str], str] = {
    ("sistema", "2026-10-29.1"): "28e141939e69",
    ("sistema", "2026-10-30.1"): "c621007b282b",  # módulo 97: las propuestas (proponer_movimiento)
    ("estructura", "2026-10-29.1"): "7c4369df4cad",
    ("titulo", "2026-10-30.1"): "c5337c455f6d",  # módulo 97
    ("recuerdos", "2026-10-30.1"): "0ae9ad55872b",  # módulo 99
    ("resumen_previo", "2026-10-30.1"): "52fb9fa9232c",
    ("resumir", "2026-10-30.1"): "3d207b0b17f9",
}
