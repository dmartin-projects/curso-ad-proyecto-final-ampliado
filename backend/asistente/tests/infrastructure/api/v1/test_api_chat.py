"""Módulo 97: la API del chat de punta a punta (con la base de datos y un LLMFake en el contenedor): conversaciones,
carpetas, la pregunta en streaming, propuestas que se confirman y gráficos fijados."""

import json

import pytest

from asistente.infrastructure import container
from asistente.tests.fakes.llm_fake import LLMFake
from conftest import MembresiaFactory, UsuarioFactory
from finanzas.models import Movimiento

pytestmark = [
    pytest.mark.django_db,
    # El cliente de test es síncrono (WSGI): consume el generador asíncrono entero y avisa. En ASGI se envía a trozos
    pytest.mark.filterwarnings("ignore:StreamingHttpResponse must consume asynchronous iterators"),
]


def url(hogar, recurso="conversaciones", *resto) -> str:
    return "/".join([f"/api/v1/hogares/{hogar.pk}/asistente/{recurso}", *map(str, resto), ""])


def estructurada(texto, seguimiento=()) -> LLMFake:
    return LLMFake.responder(json.dumps({"texto": texto, "cifras": [], "seguimiento": list(seguimiento)}))


@pytest.fixture
def llm(monkeypatch, settings):
    """El modelo de la pregunta y el auxiliar (el título), con guion: lo que el test meta en .guion."""
    settings.ASISTENTE_API_KEY = "fake"
    principal, auxiliar = LLMFake([]), LLMFake([LLMFake.responder("Gasto de septiembre")])
    monkeypatch.setattr(container, "llm", lambda modelo=None: principal)
    monkeypatch.setattr(container, "llm_auxiliar", lambda: auxiliar)
    return principal


def eventos(respuesta) -> list[tuple[str, dict]]:
    """El cuerpo SSE, en (tipo, datos). El cliente de test consume el generador asíncrono entero."""
    texto = b"".join(respuesta).decode()
    salida = []
    for bloque in texto.strip().split("\n\n"):
        if bloque.startswith(":"):
            continue
        tipo, datos = bloque.split("\n")
        salida.append((tipo.removeprefix("event: "), json.loads(datos.removeprefix("data: "))))
    return salida


def test_una_conversacion_de_punta_a_punta(casa, cliente, llm):
    ana, hogar = casa
    c = cliente(ana)
    creada = c.post(url(hogar), {}, format="json")
    assert creada.status_code == 201
    cid = creada.json()["conversacion"]["id"]
    llm.guion += [
        LLMFake.llamar("gasto_por_categoria", mes="2026-09"),
        LLMFake.responder("En septiembre, 776,59 €."),
        estructurada("En septiembre, 776,59 €.", ["¿Y en agosto?"]),
    ]

    r = c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "¿Cuánto en septiembre?"}, format="json")
    assert r.status_code == 200 and r["Content-Type"] == "text/event-stream; charset=utf-8"
    assert r["Cache-Control"] == "no-cache" and r["X-Accel-Buffering"] == "no"
    tipos = [t for t, _ in eventos(r)]
    assert tipos == ["inicio", "tool", "texto", "titulo", "fin"]

    leida = c.get(url(hogar, "conversaciones", cid)).json()
    assert leida["conversacion"]["titulo"] == "Gasto de septiembre"
    assert [(m["rol"], m["texto"]) for m in leida["mensajes"]] == [
        ("usuario", "¿Cuánto en septiembre?"),
        ("modelo", "En septiembre, 776,59 €."),
    ]
    assert leida["mensajes"][1]["datos"]["seguimiento"] == ["¿Y en agosto?"]
    assert [x["titulo"] for x in c.get(url(hogar)).json()] == ["Gasto de septiembre"]


def test_la_conversacion_de_otro_es_un_404_antes_de_empezar(casa, cliente, llm):
    ana, hogar = casa
    luis = UsuarioFactory()
    MembresiaFactory(hogar=hogar, usuario=luis, rol="admin")
    cid = cliente(ana).post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    r = cliente(luis).post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "hola"}, format="json")
    assert r.status_code == 404 and r["Content-Type"] == "application/json"
    assert cliente(luis).get(url(hogar, "conversaciones", cid)).status_code == 404
    assert llm.peticiones == []


def test_un_adjunto_que_no_es_una_foto_ni_un_pdf(casa, cliente, llm):
    from django.core.files.uploadedfile import SimpleUploadedFile

    ana, hogar = casa
    cid = cliente(ana).post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    archivo = SimpleUploadedFile("virus.exe", b"MZ", content_type="application/octet-stream")
    r = cliente(ana).post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "mira", "archivo": archivo})
    assert r.status_code == 400 and "archivo" in r.json()["errors"]


def test_carpetas_y_mover_una_conversacion(casa, cliente):
    ana, hogar = casa
    c = cliente(ana)
    carpeta = c.post(url(hogar, "carpetas"), {"nombre": "Viaje"}, format="json").json()
    assert c.post(url(hogar, "carpetas"), {"nombre": "Viaje"}, format="json").status_code == 400
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    movida = c.patch(url(hogar, "conversaciones", cid), {"carpeta": carpeta["id"], "titulo": "Lisboa"}, format="json")
    assert movida.json()["conversacion"] | {"actualizada": None} == {
        "id": cid,
        "titulo": "Lisboa",
        "carpeta": carpeta["id"],
        "actualizada": None,
    }
    assert c.get(url(hogar, "carpetas")).json() == [{"id": carpeta["id"], "nombre": "Viaje", "conversaciones": 1}]
    assert [x["id"] for x in c.get(url(hogar), {"carpeta": carpeta["id"]}).json()] == [cid]
    assert c.delete(url(hogar, "carpetas", carpeta["id"])).status_code == 204
    assert c.get(url(hogar, "conversaciones", cid)).json()["conversacion"]["carpeta"] is None


def test_una_propuesta_confirmada_apunta_el_gasto_con_el_rol_de_quien_confirma(casa, cliente, llm):
    ana, hogar = casa
    c = cliente(ana)
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    llm.guion += [
        LLMFake.llamar("proponer_movimiento", importe="3.50", concepto="Churros", categoria="Ocio"),
        LLMFake.responder("Preparado: confírmalo."),
        estructurada("Preparado: confírmalo."),
    ]
    (propuesta,) = [
        d
        for t, d in eventos(
            c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "Apunta 3,50 de churros"}, format="json")
        )
        if t == "propuesta"
    ]
    antes = Movimiento.objects.count()

    r = c.post(url(hogar, "propuestas", propuesta["id"], "confirmar"))
    assert r.status_code == 200 and r.json()["estado"] == "confirmada"
    m = Movimiento.objects.get(pk=r.json()["resultado"]["movimiento_id"])
    assert (Movimiento.objects.count(), m.importe, m.concepto, m.categoria.nombre) == (
        antes + 1,
        -3.5,
        "Churros",
        "Ocio",
    )
    assert c.post(url(hogar, "propuestas", propuesta["id"], "confirmar")).status_code == 409  # el doble clic
    leida = c.get(url(hogar, "conversaciones", cid)).json()
    assert leida["mensajes"][1]["datos"]["propuestas"][0]["estado"] == "confirmada"


def test_un_lector_puede_preguntar_pero_no_confirmar(casa, cliente, llm):
    ana, hogar = casa
    lector = UsuarioFactory()
    MembresiaFactory(hogar=hogar, usuario=lector, rol="lector")
    c = cliente(lector)
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    llm.guion += [
        LLMFake.llamar("proponer_movimiento", importe="1", concepto="Pan"),
        LLMFake.responder("Preparado."),
        estructurada("Preparado."),
    ]
    respuesta = c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "Apunta 1 € de pan"}, format="json")
    (propuesta,) = [d for t, d in eventos(respuesta) if t == "propuesta"]
    assert c.post(url(hogar, "propuestas", propuesta["id"], "confirmar")).status_code == 403
    assert cliente(ana).post(url(hogar, "propuestas", propuesta["id"], "confirmar")).status_code == 404  # no es suya


def test_fijar_un_grafico_lo_ven_todos_recalculado(casa, cliente):
    ana, hogar = casa
    lector = UsuarioFactory(nombre="Luis")
    MembresiaFactory(hogar=hogar, usuario=lector, rol="lector")
    especificacion = {
        "tipo": "barras",
        "titulo": "Septiembre",
        "fuente": "gasto_por_categoria",
        "argumentos": {"mes": "2026-09"},
    }
    assert cliente(lector).post(url(hogar, "graficos-fijados"), especificacion, format="json").status_code == 403
    fijado = cliente(ana).post(url(hogar, "graficos-fijados"), especificacion, format="json")
    assert fijado.status_code == 201
    (visto,) = cliente(lector).get(url(hogar, "graficos-fijados")).json()
    assert (visto["fijado_por"], visto["grafico"]["etiquetas"][0], visto["error"]) == ("Ana", "Supermercado", None)
    otra = {**especificacion, "fuente": "buscar_movimientos"}
    assert cliente(ana).post(url(hogar, "graficos-fijados"), otra, format="json").status_code == 400
    assert cliente(ana).delete(url(hogar, "graficos-fijados", visto["id"])).status_code == 204


def test_borrar_la_conversacion_borra_el_csv_de_una_pregunta_que_no_termino(casa, cliente, llm):
    """El CSV se guarda al ejecutar `exportar`; el modelo cae después. Sin ligarlo a la pregunta en ese momento,
    quedaría en el almacenamiento un archivo con movimientos del hogar que nada enseña ni borra."""
    from django.core.files.storage import default_storage

    from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException

    ana, hogar = casa
    c = cliente(ana)
    cid = c.post(url(hogar), {}, format="json").json()["conversacion"]["id"]
    llm.guion += [LLMFake.llamar("exportar", desde="2026-09-01", hasta="2026-09-30"), LLMNoDisponibleException("caído")]
    r = c.post(url(hogar, "conversaciones", cid, "preguntar"), {"texto": "Los movimientos en CSV"}, format="json")
    assert [t for t, _ in eventos(r)] == ["inicio", "tool", "archivo", "error"]
    carpeta = f"asistente/{hogar.pk}/exportaciones"
    assert len(default_storage.listdir(carpeta)[1]) == 1

    assert c.delete(url(hogar, "conversaciones", cid)).status_code == 204
    assert default_storage.listdir(carpeta)[1] == []
