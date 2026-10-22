# core/infrastructure/signals/red_de_seguridad.py — receivers de "red de seguridad" mientras dura la migración
# (módulos 87 y 88)
#
# Los use cases publican sus eventos EXPLÍCITAMENTE (outbox y avisos internos). Pero hasta el módulo 88 aún hay
# código que guarda movimientos sin pasar por ellos (tickets, importaciones, backoffice, el admin, los borrados
# en cascada), y para ese código siguen los receivers de post_save / post_delete. Para no publicar dos veces,
# el repositorio marca las instancias que guarda un use case y los receivers las saltan.
_ATRIBUTO = "_eventos_del_caso_de_uso"


def publicados_por_caso_de_uso(instancia):
    """Marca la instancia de Django: sus eventos los publica el use case, no los receivers."""
    setattr(instancia, _ATRIBUTO, True)
    return instancia


def lo_publica_un_caso_de_uso(instancia) -> bool:
    return getattr(instancia, _ATRIBUTO, False)
