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
├── migrations/           en la raíz de la app, como siempre
├── management/commands/  donde Django los busca (son adapters de entrada)
└── tests/                en espejo: domain/bo, domain/services, application, infrastructure/api/v1,
                          infrastructure/database/{models,repositories}, fakes/
```

`core` es el **shared kernel**, con las mismas carpetas: `core/domain/{vo,enums,exceptions,services,bo,read_models,
repositories/queries}` (`Dinero`, `Mes`, `Actor`, `Rol`, `Accion`, `DominioException` y sus subclases, `diferencias`,
`IAuditable`, `Pagina[T]`, `Paginacion`, `PaginacionCursor`), `core/application/dtos/` (`PaginaOutputDTO[T]`),
`core/application/ports/` (`IUnidadDeTrabajo`, `IPublicadorEventos`, `IAuditoria`, `IReloj`) y
`core/infrastructure/` (sus adapters de Django, el *exception handler*, la paginación y las piezas de los
*serializers* que llaman al dominio). Lo que no sea de todas las apps, no va en core.

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

1. `*.domain` y `*.application` no importan django, rest_framework, drf_spectacular, django_filters, celery,
   psycopg ni opentelemetry (ni directa ni indirectamente).
2. Dentro de la app, de arriba abajo: `infrastructure.api | infrastructure.signals.receivers` →
   `infrastructure.tasks` → `infrastructure.container` → `infrastructure.messaging` → `infrastructure.cache` →
   `infrastructure.database | infrastructure.signals.finanzas_signals` → `application` → `domain`. Nunca hacia arriba.
3. `core.domain` y `core.application` no importan ninguna app.

Cada app que se reorganiza añade su contrato de capas (copia el de finanzas con sus carpetas).

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
| CRUD puro | Si un recurso no tiene reglas ni efectos (las cuentas), se queda como `ModelViewSet` sobre el ORM. Se extrae a use case con la primera regla. |

## 10. Tests en espejo

| Carpeta | Qué prueba | Base de datos |
|---|---|---|
| `tests/domain/{bo,services}/test_<módulo>.py` | Invariantes y reglas de BOs y domain services | No (pytest-django la bloquea) |
| `tests/application/test_<use_case>.py` | Orquestación de cada use case con `tests/fakes/` (`Mundo`): permisos, qué se guarda, audita y publica, rollback | No |
| `tests/fakes/` | Un fake por interfaz (`<x>_fake.py`, hereda de ella), `mundo.py` y los tests de los propios fakes | No |
| `tests/infrastructure/database/repositories/` | *Contract tests* (fake y ORM, los mismos tests) y query services | Sí |
| `tests/infrastructure/api/v1/` | La API de extremo a extremo (`test_api.py`, `test_reglas_api.py`, `test_dashboard_view.py`…) | Sí |

El *job* `arquitectura` del CI ejecuta `domain`, `application` y `fakes` sin PostgreSQL.

## 11. Mientras dure la migración (hasta el 88)

- Las apps aún sin esta estructura (tickets, importaciones, backoffice, informes, notificaciones…) siguen escribiendo
  movimientos con el ORM. Para ellas siguen los receivers de `post_save`/`post_delete` (finanzas y eventos): la
  **red de seguridad** (`core/infrastructure/signals/red_de_seguridad.py`). Lo que guarda un use case viene marcado y
  los receivers lo saltan.
- Desde fuera de finanzas se importa, de momento: `finanzas.models`, `finanzas.infrastructure.signals.finanzas_signals`,
  `finanzas.infrastructure.database.services.reconocimiento_comercios`, el `DashboardQueryServiceORM` (informes, sin use case hasta el 88) y
  `finanzas.domain.services.normalizacion`. En el 88, las escrituras de otras apps pasan a los use cases de finanzas
  (por el contenedor) y desaparece la red de seguridad.

## 12. Lo que viene

- **88**: hogares, usuarios, tickets, importaciones, informes, notificaciones, backoffice y eventos con esta misma
  estructura; tickets e importaciones crean movimientos con use cases de finanzas; el backoffice recategoriza con
  `RecategorizarMovimientosUseCase` (hoy duplica la lógica); un contrato de independencia entre apps.
- **89**: estadisticas (FastAPI) con el mismo árbol: `domain`, `application/<use_case>/` con DTOs de Pydantic,
  `infrastructure/{api/v1/{routers,schemas}, database/{models,repositories}, messaging}`, un `APIRouter` por módulo
  montado en `infrastructure/api/app.py`, y el contenedor como composition root.
