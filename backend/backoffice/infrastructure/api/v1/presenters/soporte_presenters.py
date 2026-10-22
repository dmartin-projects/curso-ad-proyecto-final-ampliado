# backoffice/infrastructure/api/v1/presenters/soporte_presenters.py — de los OutputDTOs a lo que leen los serializers (módulo 88)
#
# Los serializers son los de siempre (ModelSerializers: el esquema OpenAPI sale de ellos) y leen atributos con la
# forma de los modelos: hogar.pk, hogar.nombre, subido_por.email, content_type.app_label… Los presenters les dan
# esa forma a partir de los OutputDTOs.
from types import SimpleNamespace as N


def _campos(dto, *fuera: str) -> dict:
    return {c: getattr(dto, c) for c in dto.__dataclass_fields__ if c not in fuera}


def ticket(t) -> N:
    campos = _campos(t, "hogar_id", "hogar_nombre", "subido_por_email")
    subido_por = None if t.subido_por_email is None else N(email=t.subido_por_email)
    return N(pk=t.id, hogar=N(pk=t.hogar_id, nombre=t.hogar_nombre), subido_por=subido_por, **campos)


def importacion(i) -> N:
    return N(pk=i.id, hogar=N(pk=i.hogar_id, nombre=i.hogar_nombre), **_campos(i, "hogar_id", "hogar_nombre"))


def hogar(h) -> N:
    miembros = [N(usuario_id=m.usuario_id, usuario=N(email=m.email), rol=m.rol) for m in h.miembros]
    return N(pk=h.id, membresias=miembros, **_campos(h, "miembros"))


def usuario(u) -> N:
    return N(pk=u.id, **_campos(u))


def movimiento(m) -> N:
    categoria = None if m.categoria_id is None else N(pk=m.categoria_id, nombre=m.categoria_nombre)
    campos = _campos(m, "hogar_id", "categoria_id", "categoria_nombre")
    return N(pk=m.id, hogar=N(pk=m.hogar_id), categoria=categoria, **campos)


def registro(r) -> N:
    app_label, _, modelo = r.modelo.partition(".")
    usuario_ = None if r.usuario_email is None else N(email=r.usuario_email)
    campos = _campos(r, "usuario_email", "modelo")
    return N(pk=r.id, usuario=usuario_, content_type=N(app_label=app_label, model=modelo), **campos)


def tarea(t) -> N:
    return N(pk=t.id, crontab=t.horario, **_campos(t, "horario"))
