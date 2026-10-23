# usuarios/domain/enums/proposito.py — para qué se va al proveedor (módulo 91)
from enum import StrEnum


class Proposito(StrEnum):
    ENTRAR = "entrar"  # en la pantalla de login: entrar (o crear la cuenta)
    VINCULAR = "vincular"  # desde «Métodos de acceso», ya dentro: añadir esta forma de entrar a MI cuenta
    AUTORIZAR = "autorizar"  # ejercicio 3: entrar en el authorization server para dar acceso a una aplicación
