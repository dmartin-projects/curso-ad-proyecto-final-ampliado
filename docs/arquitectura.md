# Arquitectura del backend: hexagonal, con una estructura explícita

Módulo 87 (convenciones y `finanzas`), 88 (resto de apps de Django) y 89 (el servicio de estadísticas en FastAPI).
Si vas a tocar una app, sigue esto; si algo no encaja, cámbialo **aquí** primero.

La idea en una frase: **cada cosa tiene una carpeta y cada clase, un archivo**. Al abrir una app se ve qué *business
objects* tiene, qué *use cases* ofrece, qué interfaces necesita y qué *adapters* las cumplen, sin leer código.

## 1. El árbol de una app

```
finanzas/
├── domain/                                   Python puro: SIN Django, DRF, Celery ni base de datos
│   ├── bo/                                   business objects (entidades), uno por archivo
│   │   └── movimiento.py                     Movimiento (y las reglas sueltas que usa: comprobar_importe…)
│   ├── vo/                                   value objects inmutables (los de todas las apps, en core/domain/vo)
│   ├── enums/            origen.py           Origen
│   ├── exceptions/       importe_cero_exception.py → ImporteCeroException (una por archivo)
│   ├── events/           movimiento_registrado_event.py → MovimientoRegistradoEvent (uno por archivo)
│   ├── services/         normalizacion.py, categorias_por_defecto.py (domain services: lógica que no es de un BO)
│   ├── read_models/      movimiento_listado.py → MovimientoListado, dashboard.py → Dashboard (lo que devuelve un
│   │                     query service; frozen dataclasses; la página genérica, Pagina[T], en core)
│   └── repositories/
│       ├── i_movimiento_command_repository.py    IMovimientoCommandRepository (escritura, ABC)
│       ├── i_movimiento_query_service.py         IMovimientoQueryService (lectura, ABC: listar, detalle, exportar)
│       └── queries/      movimientos_query.py → MovimientosQuery (filtros, orden y paginación)
├── application/                              use cases; tampoco conoce Django
│   ├── registrar_movimiento_use_case/        un paquete por use case
│   │   ├── i_registrar_movimiento_use_case.py    IRegistrarMovimientoUseCase (ABC)
│   │   ├── registrar_movimiento_use_case.py      RegistrarMovimientoUseCase
│   │   └── dtos/registrar_movimiento_input_dto.py RegistrarMovimientoInputDTO
│   ├── listar_movimientos_use_case/          un use case de consulta por listado (y obtener_…, exportar_…)
│   ├── shared/
│   │   ├── dtos/movimiento_output_dto.py     MovimientoOutputDTO (el que devuelven varios use cases)
│   │   └── autorizacion_por_hogar.py         exigir_cuenta, exigir_categoria
│   └── ports/            i_reconocedor_comercios.py → IReconocedorComercios (servicios que usa la aplicación)
├── infrastructure/                           Django, DRF, Celery, Redis: los adapters
│   ├── api/v1/
│   │   ├── views/        movimiento_viewset.py → MovimientoViewSet (una view por archivo)
│   │   ├── serializers/  movimiento_serializer.py → MovimientoSerializer
│   │   ├── filters/      movimiento_filter.py → MovimientoFilter (valida los query params y da la query)
│   │   ├── presenters/   movimiento_presenter.py → presentar(OutputDTO) con la forma que lee el serializer
│   │   └── urls.py       el router de DRF de la app (sus endpoints)
│   ├── database/
│   │   ├── models/       movimiento_model.py → Movimiento (el modelo de Django; un archivo por modelo)
│   │   ├── querysets/    movimiento_queryset.py → MovimientoQuerySet
│   │   ├── mappers/      movimiento_mapper.py → movimiento_a_bo / movimiento_a_modelo
│   │   ├── repositories/ movimiento_command_repository_orm.py → MovimientoCommandRepositoryORM
│   │   │                 movimiento_query_service_orm.py → MovimientoQueryServiceORM (lectura: filtra y pagina)
│   │   └── services/     reconocedor_comercios_orm.py → ReconocedorComerciosORM (adapters de BD que no son repos)
│   ├── cache/            dashboard_cache.py → DashboardQueryServiceCache (envuelve al query service)
│   ├── messaging/        publicador_eventos_django.py → PublicadorEventosDjango (outbox + avisos internos)
│   ├── signals/          finanzas_signals.py (las Signal de la app) y receivers.py (adapter de entrada)
│   ├── tasks/            comprobar_presupuestos_task.py (Celery, con name= explícito)
│   └── container.py      composition root: una función por use case
├── models.py             puerta de entrada de los modelos: Django los busca en <app>.models
├── tasks.py              (solo si tiene tareas de django.tasks) reexporta su ruta estable: <app>.tasks.<función>
├── migrations/           en la raíz de la app, como siempre
├── management/commands/  donde Django los busca (son adapters de entrada)
└── tests/                en espejo: domain/bo, domain/services, application, infrastructure/api/v1,
                          infrastructure/database/{models,repositories}, fakes/
```

Las demás apps tienen el mismo árbol; las carpetas de `infrastructure/` que finanzas no necesita:

| Carpeta | Qué hay | Apps |
|---|---|---|
| `infrastructure/finanzas/` | El *adapter* hacia OTRA app (*anti-corruption layer*): `gastos_en_finanzas.py` → `GastosEnFinanzas(IGastos)`, `movimientos_en_finanzas.py` → `MovimientosEnFinanzas(IMovimientos)` | tickets, importaciones |
| `infrastructure/ocr/`, `ia/`, `lectores/`, `pdf/` | *Adapters* de salida a servicios externos: `LectorTesseract`, `ExtractorIA` (con su cliente, sus *serializers* de validación y sus excepciones), `LectorDeArchivos` (CSV y PDF de cualquier banco), `MaquetadorWeasyPrint` | tickets, importaciones, informes |
| `infrastructure/auth/` | Lo que ya resuelve Django detrás de un port: `PoliticaDeContrasenasDjango`, `SesionesSimpleJWT`, `EnlacesDjango` | usuarios |
| `infrastructure/websocket/` | Adapter de entrada de Channels: `consumers.py`, `middleware.py` (el ticket de un solo uso), `origenes.py`, `routing.py` | notificaciones |
| `infrastructure/realtime/`, `i18n/` | *Adapters* de salida: la *channel layer* (`tiempo_real.py`, `grupos.py`) y `TraductorDjango(ITraductor)` | notificaciones |
| `infrastructure/metrics/` | Métricas de negocio de OpenTelemetry (*gauges* que leen un use case de consulta) | tickets, eventos |
| `infrastructure/messaging/` + `relay/` | El *outbox* (`OutboxDjango(IOutbox)`), Kafka (`BrokerKafka(IBroker)`) y el *relay* que publica los pendientes | eventos |

`core` es el **shared kernel**, con las mismas carpetas: `core/domain/{vo,enums,exceptions,services,bo,read_models,
repositories/queries}` (`Dinero`, `Mes`, `Actor`, `Rol`, `Accion`, `DominioException` y sus subclases, `diferencias`,
`normalizar`, `IAuditable`, `Pagina[T]`, `Paginacion`, `PaginacionCursor`, `ListadoDelHogarQuery`),
`core/application/dtos/` (`PaginaOutputDTO[T]`), `core/application/ports/` (`IUnidadDeTrabajo`,
`IPublicadorEventos`, `IAuditoria`, `IReloj`) y `core/infrastructure/`: sus *adapters* de Django
(`database/`, `clock/`), el *exception handler* y la paginación (`api/`), las piezas que comparten las views
(`api/views/consultas.py`: los query params de un listado; `roles.py`; `health.py`), la búsqueda de los query
services (`database/busqueda.py`), las tareas (`tasks/ruta_estable.py`, `tasks/agrupar.py`), la alarma de las
escrituras sin use case (`signals/red_de_seguridad.py`), el *circuit breaker* (`cache/`), el `request_id` de los
logs (`logging/`), OpenTelemetry (`telemetry/`), la huella de un archivo (`storage/`) y el texto de una hoja de cálculo
sin fórmulas (`hojas_de_calculo/`). Sus *fakes*, que usan los tests de todas las apps, en `core/tests/fakes/`. Lo que
no sea de todas las apps, no va en core.

## 2. Nombres

| Pieza | Archivo | Clase |
|---|---|---|
| Business object | `domain/bo/movimiento.py` | `Movimiento` |
| Value object | `core/domain/vo/dinero.py` | `Dinero` |
| Enum | `domain/enums/origen.py` | `Origen` |
| Excepción | `domain/exceptions/importe_cero_exception.py` | `ImporteCeroException` |
| Evento | `domain/events/movimiento_registrado_event.py` | `MovimientoRegistradoEvent` |
| Read model | `domain/read_models/movimiento_listado.py` | `MovimientoListado` (la página: `core/domain/read_models/pagina.py` → `Pagina[T]`) |
| Query (filtros) | `domain/repositories/queries/movimientos_query.py` | `MovimientosQuery` (paginación: `core/domain/repositories/queries/paginacion.py` → `Paginacion`, `PaginacionCursor`) |
| Interfaz de escritura | `domain/repositories/i_movimiento_command_repository.py` | `IMovimientoCommandRepository` |
| Interfaz de lectura | `domain/repositories/i_movimiento_query_service.py` | `IMovimientoQueryService` |
| Interfaz del use case | `application/registrar_movimiento_use_case/i_registrar_movimiento_use_case.py` | `IRegistrarMovimientoUseCase` |
| Use case | `application/registrar_movimiento_use_case/registrar_movimiento_use_case.py` | `RegistrarMovimientoUseCase` |
| DTO de entrada | `…/dtos/registrar_movimiento_input_dto.py` | `RegistrarMovimientoInputDTO` |
| DTO de salida | `application/shared/dtos/movimiento_output_dto.py` | `MovimientoOutputDTO` |
| Port | `application/ports/i_reconocedor_comercios.py` | `IReconocedorComercios` |
| Modelo de Django | `infrastructure/database/models/movimiento_model.py` | `Movimiento` (en infraestructura se importa `as MovimientoModel`) |
| Command repository | `infrastructure/database/repositories/movimiento_command_repository_orm.py` | `MovimientoCommandRepositoryORM` |
| Query service | `infrastructure/database/repositories/movimiento_query_service_orm.py` | `MovimientoQueryServiceORM` |
| Use case de consulta | `application/listar_movimientos_use_case/listar_movimientos_use_case.py` | `ListarMovimientosUseCase` (devuelve `PaginaOutputDTO[MovimientoListadoOutputDTO]`) |
| Presenter | `infrastructure/api/v1/presenters/movimiento_presenter.py` | `presentar(dto)` |
| Mapper | `infrastructure/database/mappers/movimiento_mapper.py` | `movimiento_a_bo`, `movimiento_a_modelo` |
| View | `infrastructure/api/v1/views/movimiento_viewset.py` | `MovimientoViewSet` |
| Serializer | `infrastructure/api/v1/serializers/movimiento_serializer.py` | `MovimientoSerializer` |
| Fake de los tests | `tests/fakes/movimiento_command_repository_fake.py` | `MovimientoCommandRepositoryFake` |

- La **estructura y los sufijos, en inglés** (`bo`, `use_case`, `command_repository`, `query_service`, `InputDTO`,
  `OutputDTO`, `_model`, `_orm`, `i_`); **el dominio, en castellano** (movimiento, hogar, categoría, registrar…).
- Una clase por archivo, y el archivo se llama como la clase en `snake_case`. Las funciones que solo existen para
  esa clase (las reglas sueltas de `Movimiento`, `MesSiguiente` junto a `PresupuestoQuerySet`) se quedan con ella.
- **El modelo de Django conserva su nombre** (`Movimiento`, no `MovimientoModel`): es el nombre de la tabla
  (`finanzas_movimiento`), del `ContentType`, de los permisos y de las *migrations*. Cambiarlo sería un
  `RenameModel`. El sufijo va en el archivo y, dentro de `infrastructure/`, en el alias del `import`.
- Imports **absolutos** siempre (`from finanzas.domain.bo.movimiento import Movimiento`), sin `__init__.py` que
  reexporten: el `import` dice dónde vive cada cosa. La única puerta de entrada es `<app>/models.py`.

## 3. Quién puede importar a quién

Lo comprueba `uv run lint-imports` (contratos en `backend/pyproject.toml`, *job* `arquitectura` del CI):

1. `*.domain` y `*.application` (de todas las apps y de core) no importan django, rest_framework,
   drf_spectacular, django_filters, celery, channels, psycopg, opentelemetry, confluent_kafka, weasyprint,
   pytesseract ni httpx (ni directa ni indirectamente).
2. Dentro de cada app, de arriba abajo (un solo contrato `layers` con todas las apps como `containers`; las capas
   que una app no tiene van entre paréntesis, opcionales): `infrastructure.api | infrastructure.signals.receivers |
   infrastructure.metrics` → `infrastructure.websocket` → `infrastructure.tasks` → `infrastructure.relay` →
   `infrastructure.container` → `infrastructure.messaging | infrastructure.finanzas` → `infrastructure.cache |
   infrastructure.realtime` → `infrastructure.database | auth | ocr | ia | lectores | pdf | i18n |
   signals.<app>_signals` → `application` → `domain`. Nunca hacia arriba.
3. `core.domain` y `core.application` no importan ninguna app.
4. El núcleo de una app (`domain` + `application`) no importa ninguna otra app (un contrato `<app>-nucleo` por
   app): lo que necesita de otra es un port suyo, en sus palabras (`IGastos`, `IMovimientos`), y su
   `infrastructure/finanzas/` lo implementa con la otra.
5. Los *adapters* de una app son suyos (un contrato `protected` por app): desde fuera solo se importan su
   `container`, sus InputDTOs, su `domain`, sus modelos (`<app>.models`, para FK y lecturas), sus query services
   (`database/repositories/*_query_service_orm.py`), sus signals (`signals/<app>_signals.py`) y, de hogares,
   `api/base/` (la base de las vistas anidadas). El ACL (`infrastructure/finanzas/`) también es de su app. `config`
   monta las URLs y el ASGI.

Una app nueva se añade a `root_packages`, a `containers` del contrato de capas y con sus contratos 4 y 5.

## 4. Interfaces con `abc.ABC`, no con `typing.Protocol`

Toda interfaz (repositorios, query services, ports y use cases) es una clase `ABC` con `@abstractmethod`, y las
implementaciones **heredan** de ella: `class MovimientoCommandRepositoryORM(IMovimientoCommandRepository)`.

- **El contrato es explícito**: quien lee la implementación ve qué cumple, y el IDE salta de la interfaz a sus
  implementaciones (la del ORM y el *fake*).
- **Falla pronto**: si a una implementación le falta un método, instanciarla lanza `TypeError`; con `Protocol` solo
  lo dice un *type checker*, si alguien lo ejecuta.
- **Es la convención habitual** en proyectos FastAPI y Django hexagonales de equipos grandes: el prefijo `i_` en el
  árbol dice dónde están los contratos.

El coste: más *boilerplate* (cada *fake* hereda de su interfaz) y acoplamiento nominal. `Protocol` (*structural
typing*) es igual de válido cuando se prefiere que los *adapters* no dependan de nada; aquí se elige `ABC` por
descubribilidad.

## 5. El *composition root*: `infrastructure/container.py`

Una función por *use case* que lo devuelve montado con sus *adapters* (`registrar_movimiento()`), con la interfaz
como tipo de retorno. Es el papel de una *factory*, pero vive en **infraestructura**: una `*_factory.py` dentro de
`application/` tendría que importar los repositorios del ORM, y `application` no puede importar `infrastructure`
(regla 2 de §3). Nada de *singletons* ni de un *framework* de DI: los *adapters* no guardan estado y montar un use
case cuesta microsegundos. En un test con base de datos, una pieza se cambia con
`monkeypatch.setattr(container, "PublicadorEventosDjango", ...)`.

## 6. CQRS: escribir con BOs, leer con *query services*

| | Escritura (*command*) | Lectura (*query*) |
|---|---|---|
| *Use case* | `RegistrarMovimientoUseCase`, `ComprobarPresupuestosUseCase`… | `ListarMovimientosUseCase`, `ObtenerMovimientoUseCase`, `ObtenerDashboardUseCase`… |
| Interfaz | `domain/repositories/i_<x>_command_repository.py` | `domain/repositories/i_<x>_query_service.py` |
| Trabaja con | BOs (`obtener` → cambiar → `guardar`) | *Read models* de `domain/read_models/` |
| Implementación | `<x>_command_repository_orm.py` | `<x>_query_service_orm.py` (agregaciones, `values`, ventanas) |
| Transacción y eventos | `with self.uow:` y `self.eventos.publicar(...)` | Ninguno |

- Un *use case* de comando usa *command repositories*; uno de consulta, *query services*. No se mezclan.
- **La interfaz de lectura va en el dominio**, junto a la de escritura, y por eso devuelve *read models* del
  dominio: el dominio no puede importar `application`, así que no puede devolver un OutputDTO. El *use case* de
  consulta traduce el *read model* a su OutputDTO.
- **Todo lo que se lee pasa por esa frontera**, también los listados paginados: `IMovimientoQueryService.listar`
  recibe una `MovimientosQuery` (filtros, búsqueda, orden y una `Paginacion` por número o una `PaginacionCursor`) y
  devuelve una `Pagina[MovimientoListado]`; `detalle` y `exportar` (el CSV, un iterador) hacen lo mismo. La frontera de
  lectura es la misma para la API, un comando o una *tool* del agente (Parte 7), que no tiene paginador de DRF.
- **El ORM optimiza dentro** del *query service*: `select_related`, `annotate`, `values_list`, `iterator`, el
  `Paginator` de Django o un *keyset* para el cursor (`core/infrastructure/database/paginacion.py`). El `QuerySet` no
  sale de la infraestructura.
- **La API traduce en los dos sentidos**: los query params se validan con las piezas de siempre (django-filter,
  `OrderingFilter`, `SearchFilter`: mismos errores, mismo esquema OpenAPI) y se convierten en el InputDTO; la
  `PaginaOutputDTO` vuelve a ser el JSON de siempre con `PaginacionEstandar.respuesta()` /
  `PaginacionCursor.respuesta()` (mismos `count`, `next`, `previous`…), y cada OutputDTO pasa por su *presenter* para
  que el *serializer* de siempre lo escriba.
- La *cache* es otro *adapter* que cumple la misma interfaz: `DashboardQueryServiceCache(DashboardQueryServiceORM())`
  (patrón *decorator*), montado en `container.py`. El *use case* no sabe que existe.

## 7. La API: una por app, y un router principal que solo monta

- Cada app es dueña de sus *endpoints*: `infrastructure/api/v1/urls.py` con su `DefaultRouter`, sus `views/` y sus
  `serializers/`. Una v2 sería `infrastructure/api/v2/`, al lado.
- `config/api_v1.py` es el router principal: un `include` por app y nada más. `config/urls.py` lo monta en
  `api/<str:version>/`, porque DRF (`URLPathVersioning`) lee la versión de ahí y `ALLOWED_VERSIONS` limita cuáles
  existen.
- Frente a una carpeta `api_v1/` central para todo el proyecto (más simple al principio), la API por app escala
  mejor: cada equipo toca su app, la app se lee entera (*vertical slice*) y se puede mover a otro servicio llevándose
  sus *endpoints*.

| Pieza | Convención |
|---|---|
| View | Traduce: serializer → InputDTO (`serializer.a_dominio()`), `container.xxx().ejecutar(entrada)`, *response* desde un use case de consulta (`serializer.instance = self._leer(id)`: `container.obtener_movimiento()` + *presenter*). Los listados y el detalle, igual: `list()` y `retrieve()` llaman a su use case de consulta. Sin reglas, sin `transaction.atomic`, sin `try/except`. Los roles que exige antes de validar los lee de los use cases (`roles_de(...)`). |
| Serializer | Valida formato e ids del hogar (`DelHogarMixin`); las reglas de negocio solo las llama con `regla()` para dar todos los errores a la vez. Nada de *docstrings* que no quieras en OpenAPI. |
| Errores | Un único *exception handler* (`core/infrastructure/api/exceptions/manejador_errores.py`). Una `DominioException` con `campo` sale como error de validación (400, `errors.<campo>`). `infrastructure/api/exceptions/` en una app solo si tiene traducciones propias. |

## 8. Una petición, capa por capa: `POST /api/v1/hogares/3/movimientos/`

1. `config/urls.py` → `config/api_v1.py` → `finanzas/infrastructure/api/v1/urls.py` → `MovimientoViewSet.create`.
2. `RolEnHogar` comprueba el rol (403 antes de validar) con el `rol_minimo` de `RegistrarMovimientoUseCase`.
3. `MovimientoSerializer` valida el formato y que la cuenta y la categoría sean del hogar; llama a
   `comprobar_importe` y `comprobar_fecha` (reglas del dominio) para devolver todos los errores a la vez.
4. `perform_create` construye un `RegistrarMovimientoInputDTO` (hogar, `Actor` y `a_dominio()`) y llama a
   `container.registrar_movimiento().ejecutar(entrada)`.
5. `RegistrarMovimientoUseCase`: `actor.exigir(rol)`; `Movimiento.registrar(...)` (el BO comprueba importe, concepto
   y fecha); `with self.uow:` comprueba que cuenta y categoría son del hogar, reconoce el comercio
   (`IReconocedorComercios`), guarda (`IMovimientoCommandRepository`), audita (`IAuditoria`) y publica
   `MovimientoRegistradoEvent` (`IPublicadorEventos`); devuelve un `MovimientoOutputDTO`.
6. Detrás de cada interfaz, su *adapter*: `MovimientoCommandRepositoryORM` (*mapper* → `INSERT` en un *savepoint*),
   `AuditoriaDjango`, `PublicadorEventosDjango` (fila del *outbox* ya; `movimientos_cambiados` al confirmar),
   `UnidadDeTrabajoDjango` (`transaction.atomic`).
7. La view lee la *response* del lado de lectura: `container.obtener_movimiento()` (`ObtenerMovimientoUseCase` →
   `IMovimientoQueryService.detalle` → `MovimientoListadoOutputDTO`), el *presenter* le da la forma que lee
   `MovimientoSerializer`, y DRF la serializa. Si algo falla en el paso 5, el *handler* de core lo traduce y la transacción no deja nada.

## 9. Más convenciones

| Pieza | Convención |
|---|---|
| BO | `@dataclass(eq=False)`; invariantes en `__post_init__`; cambios con métodos (`modificar`, `colgar_de`) que validan sobre una copia (`replace`) y aplican todo o nada. Si se audita, hereda de `IAuditable` (`tipo` y `datos_auditables()`). |
| Value object | `@dataclass(frozen=True, slots=True)`; se valida al construirse; igualdad por valor. Nunca `float` para dinero. |
| Excepción | Subclase de `ValidacionException`, `NoEncontradoException`, `SinPermisoException` o `DominioException`. Con `campo = "x"` sale como error de formulario. Mensaje en castellano. |
| DTO | `@dataclass(frozen=True)`. InputDTO con `hogar_id`, `actor` y los datos (ids, no modelos; los PATCH, `cambios: dict`). OutputDTO con tipos de Python (`Decimal`, `date`), no value objects, y `desde_bo()`. Un OutputDTO que usan varios use cases, en `application/shared/dtos/`. |
| Use case | Hereda de su interfaz; `rol_minimo`, dependencias por *keyword* en `__init__` (sus interfaces) y `ejecutar(entrada)`. Devuelve un OutputDTO, una lista de OutputDTOs, un número o `None`. Orquesta; si no orquesta nada, no hace falta. |
| Command repository | Solo lo que necesita la escritura: `obtener(hogar_id, id)` (de ESE hogar o `XNoEncontradoException`), `guardar` (pone el id), `eliminar`, operaciones en bloque. Traduce constraints con `guardar_fila` (savepoint + `diag.constraint_name`). Marca las instancias con `publicados_por_caso_de_uso`. |
| Mapper | Funciones `x_a_bo(fila)` y `x_a_modelo(bo)` en `infrastructure/database/mappers/`. |
| Transacción | Solo `with self.uow` en el use case. Nada de `transaction.atomic` en views ni serializers. |
| Eventos | Dataclasses frozen en `domain/events/`, en pasado. Los publica el use case dentro de la transacción; `PublicadorEventosDjango` los traduce (outbox + `on_commit`). Un evento sin traducción lanza `TypeError`. |
| Autorización | `Actor(usuario_id, rol)` lo construye el adapter de entrada (`DelHogarViewSet.actor`; `Actor.sistema()` en tareas). Todo id externo se busca "en este hogar". |
| Tarea de Celery | Un archivo por tarea en `infrastructure/tasks/`, con `name="<app>.tasks.<función>"`. `apps.ready()` importa los receivers y las tareas. |
| Tarea de django.tasks | Un archivo en `infrastructure/tasks/` con `@ruta_estable("<app>.tasks")` debajo de `@task` (la ruta es su identidad en la cola) y un `<app>/tasks.py` que la reexporta. El publicador la encola con `import_string(RUTA).enqueue(...)`; las de Celery, por su nombre (`current_app.tasks[NOMBRE]`), sin importar `tasks/` (está por encima). |
| Excepción de un adapter | La que no es del dominio (`TransitorioIAException`, `CircuitoAbiertoException`, `SinTransaccionException`) vive en un archivo junto a su adapter, con el mismo sufijo. |
| Entre apps | Una app pide a otra con el contenedor de la otra, desde su `infrastructure/finanzas/` (*anti-corruption layer*), que traduce a sus propios tipos (un ticket habla de su `total`; finanzas, de un `importe` negativo). Escribir en las tablas de otra app con el ORM está prohibido; leerlas, con sus modelos o sus query services, no. |
| Actor de un proceso | `Actor.sistema(en_nombre_de=usuario_id)` en tareas que trabajan para alguien (lo creado queda a su nombre); `Actor.soporte(usuario_id)` en el backoffice (rol ADMIN en cualquier hogar, auditado con su usuario). |
| Escrituras sin use case | Movimientos, presupuestos, categorías y membresías tienen eventos que solo publica el use case. Sus receivers de `post_save`/`post_delete` son una alarma (`vigilar`, en `core/infrastructure/signals/red_de_seguridad.py`): lanzan `EscrituraSinCasoDeUsoException` con `EXIGIR_CASOS_DE_USO=True` (dev, tests, E2E) y en producción dejan un error en el log. El repositorio marca lo que guarda (`publicados_por_caso_de_uso`) y lo que escribe en bloque va dentro de `en_un_caso_de_uso()`; los datos de partida de un test (factories), dentro de `escrituras_directas()`. |
| Cascadas | Lo que borra la base de datos por cascada (borrar un hogar) no pasa por los use cases de los hijos: los receivers lo detectan con el argumento `origin` de `post_delete` (`es_cascada`) y publican solo lo imprescindible (tombstones). |
| Backoffice | Un adapter de entrada más, sin dominio propio: lee de TODOS los hogares con sus use cases de consulta (`backoffice/domain/repositories/i_<x>_soporte_query_service.py`) y, para cambiar algo, llama a los use cases de la app dueña con `Actor.soporte`. Los permisos son los de Django (`PermisosPorAccion`), no un `rol_minimo`. |
| CRUD puro | Si un recurso no tiene reglas ni efectos (crear y editar cuentas, `/auth/me/`, marcar notificaciones como leídas, activar un usuario o pausar una tarea desde el backoffice), se queda sobre el ORM. Se extrae a use case con la primera regla. |
| Subdominio genérico | Lo que ya resuelve Django (usuarios: hash de contraseñas, `AbstractBaseUser`, tokens de un solo uso) se usa a través de un port (`IPoliticaDeContrasenas`, `IEnlaces`, `ISesiones`), sin reescribirlo. `usuarios/managers.py` se queda donde está: las migraciones lo importan por su ruta. |

## 10. Tests en espejo

| Carpeta | Qué prueba | Base de datos |
|---|---|---|
| `tests/domain/{bo,services}/test_<módulo>.py` | Invariantes y reglas de BOs y domain services | No (pytest-django la bloquea) |
| `tests/application/test_<use_case>.py` | Orquestación de cada use case con `tests/fakes/` (`Mundo`): permisos, qué se guarda, audita y publica, rollback | No |
| `tests/fakes/` | Un fake por interfaz (`<x>_fake.py`, hereda de ella) y `mundo.py`; los de core (`AuditoriaFake`, `PublicadorEventosFake`, `UnidadDeTrabajoFake`, `RelojFake`, `AlmacenEnMemoria`), en `core/tests/fakes/` | No |
| `tests/infrastructure/database/repositories/` | *Contract tests* (fake y ORM, los mismos tests) y query services | Sí |
| `tests/infrastructure/finanzas/` | *Contract test* del ACL: el *adapter* hacia finanzas y su fake, con los mismos tests | Sí |
| `tests/infrastructure/api/v1/` | La API de extremo a extremo (`test_api.py`, `test_reglas_api.py`, `test_dashboard_view.py`…) | Sí |

El *job* `arquitectura` del CI ejecuta `./*/tests/domain` y `./*/tests/application` (el shared kernel y todas las
apps) sin PostgreSQL.

## 11. Las apps y sus relaciones

| App | Escribe con use cases | Necesita de otras apps (sus ports) | Ofrece |
|---|---|---|---|
| finanzas | movimientos, categorías, presupuestos, cuentas (al borrar) | — | su contenedor (también `apuntar_movimientos`, `conciliar_…`, `eliminar_movimientos`, `descartar_propuestos`), query services, `finanzas_signals` |
| hogares | hogares, membresías, invitaciones | — | su contenedor, query services, `hogares_signals`, `api/base/` |
| usuarios | registro, recuperación, contraseña | — | `usuarios.models` |
| tickets | tickets | `IGastos` → finanzas | `tickets_signals`, `TicketQueryServiceORM` (los atascados) |
| importaciones | importaciones y sus filas | `IMovimientos` → finanzas | `importaciones_signals` |
| informes | informes mensuales | lee el dashboard y los movimientos del mes (query services de finanzas) | `informes_signals` |
| notificaciones | notificaciones | `IDestinatarios` (usuarios y membresías, por sus modelos) | — (escucha las signals de las demás) |
| eventos | el outbox | — | `IOutbox` (lo usan los publicadores de finanzas y hogares) |
| backoffice | nada propio | los use cases de tickets, importaciones y finanzas, con `Actor.soporte` | — |

- Los procesos crean y borran movimientos con los use cases de finanzas, así que cada cambio tiene sus eventos
  (outbox de Kafka, avisos, comprobación de presupuestos) y, si lo pide una persona, su auditoría.
- Lo que una app avisa a otra va por sus signals (`<app>_signals.py`), que emite su publicador al confirmar la
  transacción. Quien escucha (las notificaciones) no sabe nada de cómo se produjo.

## 12. El servicio de estadísticas (FastAPI)

**El mismo árbol que una app de Django**, a propósito: quien sabe dónde está algo en `finanzas` sabe dónde está en
`estadisticas/estadisticas/`. Cambian los *adapters* (FastAPI, SQLAlchemy, Kafka) y nada más.

```
estadisticas/estadisticas/
├── domain/                                   Python puro: ni FastAPI, ni SQLAlchemy, ni Kafka, ni Pydantic
│   ├── bo/               movimiento.py → Movimiento, membresia.py → Membresia (fotos con versión, frozen)
│   ├── vo/               mes.py → Mes, periodo.py → Periodo
│   ├── enums/            topic.py → Topic, resultado.py → Resultado
│   ├── exceptions/       evento_invalido_exception.py → EventoInvalidoException (y EsquemaDesconocido…,
│   │                     ConsumidorActivo…, MesMalFormado…): cada una con su decisión (aparcar, parar, 422)
│   ├── events/           movimiento_guardado_event.py → MovimientoGuardadoEvent (y los otros tres); evento.py: la unión
│   ├── services/         interpretacion.py (interpretar: de un mensaje a un evento), medias_por_dia.py
│   ├── read_models/      mes_de_tendencia.py → MesDeTendencia, mes_sin_revisar.py → MesSinRevisar
│   └── repositories/
│       ├── i_movimiento_command_repository.py    IMovimientoCommandRepository (y membresía, progreso)
│       ├── i_movimiento_query_service.py         IMovimientoQueryService (y membresía, progreso)
│       └── queries/      periodo_del_hogar_query.py → PeriodoDelHogarQuery
├── application/
│   ├── procesar_lote_use_case/               i_…, procesar_lote_use_case.py, dtos/procesar_lote_input_dto.py
│   ├── reconstruir_proyeccion_use_case/      i_…, reconstruir_proyeccion_use_case.py
│   ├── obtener_tendencia_use_case/           i_…, obtener_tendencia_use_case.py, dtos/ (input y outputs, Pydantic)
│   ├── obtener_dias_semana_use_case/, obtener_sin_revisar_use_case/
│   ├── shared/           dtos/mensaje_input_dto.py → MensajeInputDTO (un mensaje de Kafka sin Kafka), mes_hasta.py
│   └── ports/            i_unidad_de_trabajo.py, i_aparcados.py, i_trazas.py (+ i_traza.py),
│                         i_grupo_de_consumidores.py, i_reloj.py
├── infrastructure/
│   ├── api/
│   │   ├── app.py        crear_app(): el router principal (monta v1 con su prefijo y los exception handlers)
│   │   ├── dependencies/ usuario_actual.py (el JWT de Django), hogar_permitido.py (Hogar: 404 si no eres miembro)
│   │   ├── exceptions/   mes_mal_formado_handler.py (MesMalFormadoException → 422)
│   │   └── v1/
│   │       ├── routers/  tendencia_router.py → tendencia() (un endpoint por archivo; y salud, dias_semana…)
│   │       ├── schemas/  tendencia_schema.py → Tendencia (el contrato OpenAPI; un schema por archivo)
│   │       ├── router.py el APIRouter de la v1: reúne los de routers/ (el urls.py de Django)
│   │       └── parametros.py  Meses (query param con sus límites)
│   ├── database/
│   │   ├── models/       movimiento_model.py → MovimientoModel (SQLAlchemy 2), base.py → Base
│   │   ├── repositories/ movimiento_command_repository_sql.py → MovimientoCommandRepositorySQL
│   │   │                 movimiento_query_service_sql.py → MovimientoQueryServiceSQL
│   │   ├── metadata.py   puerta de entrada de los modelos (la leen Alembic y el test de migraciones)
│   │   └── unidad_de_trabajo_sql.py, sesiones.py, guardado.py (DataError → EventoInvalidoException), conexion.py
│   ├── consumer/         consumidor_kafka.py (adapter de entrada: el bucle de Kafka)
│   ├── cli/              reconstruir_cli.py (adapter de entrada: línea de comandos)
│   ├── messaging/        aparcados_kafka.py → AparcadosKafka, grupo_kafka.py → GrupoKafka (adapters de salida)
│   ├── metrics/          retraso_consumidor.py (el gauge del retraso, que publica la API)
│   ├── telemetry/        telemetria.py, trazas_otel.py → TrazasOTel, traza_otel.py → TrazaOTel
│   ├── clock/            reloj_sistema.py → RelojSistema
│   └── container.py      composition root: una función por use case (y las dependencias de FastAPI)
├── ajustes.py            configuración (pydantic-settings). Solo la leen el container y la infraestructura
└── api.py, consumidor.py, reconstruir.py     puntos de entrada (uvicorn, python -m): los comandos de siempre
```

`migraciones/` (Alembic) y `tests/` (en espejo: `domain/{services,vo}`, `application`, `fakes`,
`infrastructure/{api/v1,database/{models,repositories},consumer,telemetry}`) están en la raíz del proyecto.

| Pieza | Django (§1-§11) | FastAPI (este servicio) |
|---|---|---|
| Entrada HTTP | `views/` (una view por archivo) | `routers/` (un endpoint por archivo, con su `APIRouter`) |
| Contrato de la API | `serializers/` | `schemas/` (Pydantic): el nombre de la clase es el del esquema en OpenAPI, por eso no lleva sufijo (como el modelo de Django) |
| Rutas de la app | `infrastructure/api/v1/urls.py` (`DefaultRouter`) | `infrastructure/api/v1/router.py` (`APIRouter` que incluye los de `routers/`) |
| Router principal | `config/api_v1.py` (un `include` por app) | `infrastructure/api/app.py` (`app.include_router(v1, prefix="/estadisticas/v1")`) |
| Errores del dominio → HTTP | El *exception handler* de DRF (`core/infrastructure/api/exceptions/`) | `infrastructure/api/exceptions/` con `app.add_exception_handler` |
| Autorización por hogar | `HogarDesdeUrlMixin` / `RolEnHogar` (adapter de entrada) | La dependencia `hogar_permitido` (`Hogar`), que lee `IMembresiaQueryService` |
| DTOs | `@dataclass(frozen=True)` | Pydantic con `ConfigDict(frozen=True)`; Pydantic prohibido en `domain` |
| Modelos de la BD | Django ORM, `<app>/models.py` como puerta de entrada; la clase conserva su nombre | SQLAlchemy 2, `<x>_model.py` → `<X>Model`; puerta de entrada `database/metadata.py` (el nombre de la clase no está en las migraciones) |
| Implementaciones | `*_orm.py` → `…ORM` | `*_sql.py` → `…SQL` (SQLAlchemy + PostgreSQL) |
| Transacción | `UnidadDeTrabajoDjango` (`atomic`): la de la conexión | `UnidadDeTrabajoSQL(sesion)`: la de una `Session`, que el container comparte con los repositorios; `savepoint()` es `begin_nested()` |
| Migraciones | `makemigrations --check` | `alembic check` y `tests/infrastructure/database/models/test_migraciones.py` |
| Composition root | `container.py`, una función por use case que llaman las views | `container.py`, igual; los routers la piden con `Depends(container.obtener_tendencia)` y esas funciones piden a su vez `Depends(container.sesion)` y `Depends(container.reloj)` |
| Cambiar una pieza en un test | `monkeypatch.setattr(container, …)` | Lo mismo, y en la API `app.dependency_overrides[container.reloj]` |
| Procesos y comandos | `management/commands/`, `tasks/` | `consumer/`, `cli/` y los puntos de entrada de la raíz |

Una petición, capa por capa: `GET /estadisticas/v1/hogares/1/tendencia?meses=3`

1. `infrastructure/api/app.py` → `v1/router.py` → `v1/routers/tendencia_router.py` → `tendencia()`.
2. FastAPI resuelve las dependencias, en orden: `Hogar` (`usuario_actual` comprueba el JWT: 401; `hogar_permitido`
   pregunta a `IMembresiaQueryService`: 404), y después `container.obtener_tendencia`, que monta
   `ObtenerTendenciaUseCase` con la `Session` de la petición (`container.sesion`) y el reloj (`container.reloj`).
   Por último valida los *query params* (`meses`: 422).
3. El router traduce los parámetros a un `ObtenerTendenciaInputDTO` y llama a `caso.ejecutar(entrada)`.
4. `ObtenerTendenciaUseCase` decide el periodo con el dominio (`mes_hasta` → `Mes`, `Periodo.de_meses`) y pide los
   meses a `IMovimientoQueryService.tendencia(PeriodoDelHogarQuery)` y la hora del último evento a
   `IProgresoQueryService`; traduce los *read models* a `TendenciaOutputDTO`. Un `hasta` mal formado sale como
   `MesMalFormadoException` y el *handler* de `api/exceptions/` lo convierte en 422.
5. `MovimientoQueryServiceSQL` agrupa en PostgreSQL (`date_trunc`, `CASE`) y devuelve un `MesDeTendencia` por mes.
6. El router convierte el OutputDTO en el *schema* `Tendencia` (`model_validate(dto, from_attributes=True)`) y FastAPI
   lo serializa. Al terminar la petición, `container.sesion` cierra la `Session`.

Contratos de import-linter (`estadisticas/pyproject.toml`, *steps* del *job* `estadisticas` del CI):

1. `domain` y `application` no importan fastapi, starlette, sqlalchemy, psycopg, confluent_kafka, opentelemetry, jwt,
   pydantic_settings ni `estadisticas.ajustes`. `domain`, además, ni pydantic.
2. Capas, de arriba abajo: puntos de entrada → `infrastructure.api | consumer | cli` → `infrastructure.container` →
   `infrastructure.telemetry` → `infrastructure.database | messaging | metrics | clock` → `application` → `domain`.
3. Los paquetes de los *use cases* son independientes entre sí: lo que comparten va en `application/shared` o en
   `ports`.

El CI ejecuta `tests/domain`, `tests/application` y `tests/fakes` sin PostgreSQL ni Kafka (con `DATABASE_URL` y
`KAFKA_BOOTSTRAP_SERVERS` apuntando a puertos cerrados) y después `tests/infrastructure` con los dos.
