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
| `infrastructure/auth/` | Lo que ya resuelve Django detrás de un port: `PoliticaDeContrasenasDjango`, `EnlacesDjango`, `TokensSimpleJWT` | usuarios |
| `infrastructure/providers/`, `cache/` | El social login (módulo 91): un *adapter* por proveedor de identidad (`Google`, `GitHub`, `Apple` sobre `ProveedorOIDC` y `ClienteOAuth`, con Authlib y joserfc) y `ProveedoresConfigurados(IProveedores)`; la transacción entre la ida y la vuelta, en la caché (`TransaccionesEnCache`; desde el módulo 92, también el login a medias y los retos de WebAuthn: `PendientesEnCache`, `RetosEnCache`) | usuarios |
| `infrastructure/mfa/` | El segundo factor (módulo 92): TOTP con pyotp (`TotpPyotp`), las passkeys con py_webauthn (`WebAuthnDuo`) y el QR del alta (`CodigoQrSegno`). Los secretos TOTP se cifran en `database/cifrado.py`; las sesiones y los códigos de recuperación son *adapters* de BD que no son repositorios (`database/services/`: `SesionesORM`, `CodigosDeRecuperacionORM`) | usuarios |
| `infrastructure/api/{authentication,permissions,sessions}/` | Lo que usuarios ofrece a las demás apps (módulo 92): `JWTConSesion` (el access de una sesión cerrada ya no vale), `AutenticacionReciente` (el *step-up*) y la sesión de Django de las páginas del *authorization server* atada a su sesión de Gastos | usuarios |
| `infrastructure/websocket/` | Adapter de entrada de Channels: `consumers.py`, `middleware.py` (el ticket de un solo uso), `origenes.py`, `routing.py` | notificaciones |
| `infrastructure/realtime/`, `i18n/` | *Adapters* de salida: la *channel layer* (`tiempo_real.py`, `grupos.py`) y `TraductorDjango(ITraductor)` | notificaciones |
| `infrastructure/metrics/` | Métricas de negocio de OpenTelemetry (*gauges* que leen un use case de consulta) | tickets, eventos |
| `infrastructure/messaging/` + `relay/` | El *outbox* (`OutboxDjango(IOutbox)`), Kafka (`BrokerKafka(IBroker)`) y el *relay* que publica los pendientes | eventos |
| `infrastructure/web/` | Adapter de entrada con páginas de Django: el login, el segundo factor (módulo 92) y el consentimiento del *authorization server* (`views/`, `urls.py`, `templates/`, y `middleware/`: su sesión sigue a la de Gastos) y los *endpoints* de django-oauth-toolkit (módulo 90) | oauth |
| `infrastructure/server/`, `crypto/` | Lo que se enchufa en los ajustes de django-oauth-toolkit (`ValidadorGastos`, `ScopesPorCliente`, los generadores de tokens) y la clave que firma los ID tokens | oauth |
| `infrastructure/api/{authentication,permissions,views}/` | La API como *resource server*: `AutenticacionOAuth`, `ScopeRequerido`, `EsServicio` y el *mixin* `AceptaOAuth`, que usan las views de las demás apps | oauth |
| `infrastructure/llm/` | El LLM del asistente (módulos 93 y 94): `OpenAICompatibleLLM(ILLM)` sobre la API Chat Completions con el SDK `openai` (Groq por defecto; cualquier proveedor compatible cambiando la URL, la clave y el modelo), los reintentos con tenacity, el cliente HTTP del proceso (`cliente_openai.py`) y `LLMConReserva(ILLM)`, que prueba los modelos en orden con un *circuit breaker* por modelo (un 429 lo abre el tiempo que pide el proveedor). Con el mismo cliente, `DetectorPromptGuard(IDetectorDeInyeccion)` (módulo 102): Llama Prompt Guard 2 en Groq, que devuelve la probabilidad de que un texto sea una inyección. En los tests, `LLMFake` (`tests/fakes/llm_fake.py`) y cassettes de llamadas reales | asistente |
| `infrastructure/finanzas/`, `hogares/` (en asistente) | El *anti-corruption layer* del agente (módulo 94): `ConsultasEnFinanzas(IConsultasDeFinanzas)` llama a los *use cases* de **consulta** de finanzas con el `Actor` de quien pregunta y traduce sus OutputDTOs a los *read models* del asistente; `MembresiasEnHogares(IMembresias)` lee el hogar y el rol con el *query service* de hogares; `TicketsEnTickets(ITickets)` (módulo 95) da lo que leyó la IA de un ticket del hogar, que las *tools* marcan como no fiable | asistente |
| `infrastructure/externos/` (en asistente) | Los servicios públicos de las *tools* (módulo 95): `TipoDeCambioFrankfurter(ITipoDeCambio)`, los tipos de referencia del BCE, e `IndiceDePreciosEurostat(IIndiceDePrecios)`, el IPC armonizado de España por grupo ECOICOP (`prc_hicp_minr`, el mismo índice que publica el INE). Lo común en `ServicioHttp`: httpx con *timeout* corto, reintentos con tenacity solo de lo transitorio y un *circuit breaker* por servicio; en cada *adapter*, la caché de Django según cómo cambia su dato y los errores traducidos (un fallo, `ServicioExternoNoDisponibleException`, que el agente le explica al modelo) | asistente |
| `infrastructure/api/v1/streaming/`, `storage/` (en asistente) | El chat (módulo 97): la vista de la pregunta devuelve una `StreamingHttpResponse` con un generador **asíncrono** (`transmitir.py`) que ejecuta el *use case* en un hilo y le pasa un `EmisorSSE(IEmisorDeEventos)`: los eventos cruzan del hilo al bucle de asyncio con `call_soon_threadsafe`, hay latidos y, si la persona se va, el emisor queda cancelado y el *use case* para. `AlmacenDjango(IAlmacenDeArchivos)` guarda adjuntos y exportaciones en el almacenamiento de la app. El *anti-corruption layer* crece: `ExportadorEnFinanzas`, `EjecutorDePropuestasEnFinanzas` (el `RegistrarMovimientoUseCase` de finanzas con el `Actor` de quien confirma) y `LectorDeAdjuntosEnTickets` (el OCR que tickets ofrece en su contenedor) | asistente |
| `infrastructure/telemetria/`, `tarifas/` (en asistente) | Medir el asistente (módulo 98): `LLMMedido(ILLM)`, un *decorator* de cada modelo (dentro de la reserva) que abre el *span* `chat {modelo}` y registra las métricas GenAI de OpenTelemetry (duración, primer trozo, *tokens* de entrada, salida, caché y razonamiento) y el coste; `TelemetriaOTel(ITelemetriaDelAgente)`, los *spans* `invoke_agent asistente` y `execute_tool {tool}` con su duración. Todos los nombres en `instrumentos.py`. Sin el texto de las preguntas ni de las respuestas, y sin hogares en las métricas (cardinalidad). `TarifasDesdeAjustes(ITarifas)`: los precios de cada modelo y la cuota de cada plan (`ASISTENTE_PRECIOS`, `ASISTENTE_PLANES`). El libro de cuentas (`asistente_consumo`) y el plan de cada hogar, en `database/` | asistente |
| `infrastructure/messaging/`, `tasks/` (en asistente) | La compactación de las conversaciones (módulo 99): `ProgramadorDeCompactacionCelery(IProgramadorDeCompactacion)` encola la tarea por su nombre con `on_commit` (cuando la respuesta ya está guardada) y `compactar_conversacion_task.py`, el *adapter* de entrada, ejecuta `CompactarConversacionUseCase` con el modelo auxiliar | asistente |
| `infrastructure/embeddings/`, `ayuda/` (en asistente) | La búsqueda en la ayuda (módulo 100): `EmbeddingsFastembed(IEmbeddings)`, el modelo de embeddings en el proceso (ONNX en la CPU, un modelo por proceso), y `FuenteDeAyudaEnDisco(IFuenteDeAyuda)`, los `.md` de `asistente/ayuda/`. El índice, `IndiceDeAyudaPG(IIndiceDeAyuda)` en `database/`: pgvector (coseno, HNSW) y `tsvector` en castellano (GIN) en la misma tabla | asistente |
| `infrastructure/sql/` (en asistente) | El text-to-SQL (módulo 101): `ConsultasSQLPostgres(IConsultasSQL)` ejecuta el SQL del modelo con psycopg en una conexión NUEVA del rol `gastos_asistente_sql` (fuera del ORM), en una transacción de solo lectura con `statement_timeout` y un LIMIT por fuera; antes escribe el hogar en `asistente_sql.contexto` (por el pid de esa conexión) con la conexión de la app, y lo borra después. El rol, sus permisos por columna, la RLS de las tablas de finanzas y las vistas, en la migración `0005_consultas_sql` | asistente |

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
   pytesseract, httpx ni el SDK de un LLM (`openai`, `httpx2`) (ni directa ni indirectamente).
2. Dentro de cada app, de arriba abajo (un solo contrato `layers` con todas las apps como `containers`; las capas
   que una app no tiene van entre paréntesis, opcionales): `infrastructure.api | infrastructure.signals.receivers |
   infrastructure.metrics | infrastructure.web` → `infrastructure.websocket` → `infrastructure.tasks` →
   `infrastructure.relay` → `infrastructure.container` → `infrastructure.messaging | infrastructure.finanzas |
   infrastructure.server | infrastructure.providers` → `infrastructure.cache | infrastructure.realtime` → `infrastructure.database | auth |
   crypto | mfa | ocr | ia | lectores | pdf | i18n | signals.<app>_signals` → `application` → `domain`. Nunca hacia
   arriba.
3. `core.domain` y `core.application` no importan ninguna app.
4. El núcleo de una app (`domain` + `application`) no importa ninguna otra app (un contrato `<app>-nucleo` por
   app): lo que necesita de otra es un port suyo, en sus palabras (`IGastos`, `IMovimientos`), y su
   `infrastructure/finanzas/` lo implementa con la otra.
5. Los *adapters* de una app son suyos (un contrato `protected` por app): desde fuera solo se importan su
   `container`, sus InputDTOs, su `domain`, sus modelos (`<app>.models`, para FK y lecturas), sus query services
   (`database/repositories/*_query_service_orm.py`), sus signals (`signals/<app>_signals.py`); de hogares,
   `api/base/` (la base de las vistas anidadas), y de oauth, `api/authentication/`, `api/permissions/` y
   `api/views/acepta_oauth.py` (la autenticación OAuth y los scopes de la API); de usuarios (módulo 92),
   `api/authentication/`, `api/permissions/` y `api/sessions/` (el JWT con su sesión, el *step-up* y la sesión de
   Django del *authorization server*). El ACL (`infrastructure/finanzas/`) también es de su app. `config` monta las
   URLs y el ASGI.
6. (Módulo 91) En `usuarios`, solo `infrastructure/providers` importa Authlib, joserfc o httpx: ninguna view,
   repositorio o *adapter* de cuentas habla directamente con Google, GitHub o Apple (ni toca sus tokens). Authlib y
   joserfc, además, prohibidos en todos los núcleos (regla 1).
7. (Módulo 92) En `usuarios`, solo `infrastructure/mfa` importa pyotp, webauthn (py_webauthn) o segno: las firmas de
   las passkeys y los códigos TOTP se comprueban detrás de sus ports (`IWebAuthn`, `ITotp`), en un solo sitio. Esas
   librerías y `cryptography`, además, prohibidas en todos los núcleos (regla 1).
8. (Módulos 93 y 95) En `asistente`, solo `infrastructure/llm` importa el SDK `openai`, su cliente HTTP (`httpx2`) o
   tenacity: el resto del asistente habla con el modelo a través del port `ILLM`, con los tipos de su dominio
   (`PeticionLLM`, `Mensaje`, `RespuestaLLM`). Su dominio es Python puro: ni siquiera pydantic. Con los servicios
   públicos de las *tools* (Frankfurter, Eurostat) habla `infrastructure/externos`, con httpx y tenacity, detrás de
   sus ports (`ITipoDeCambio`, `IIndiceDePrecios`): ni el contenedor ni los demás *adapters* los importan.

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
| Autorización | `Actor(usuario_id, rol)` lo construye el adapter de entrada (`HogarDesdeUrlMixin.actor`, con `actor_de` de `hogares/infrastructure/api/base/actor_de.py`; `Actor.sistema()` en tareas). Todo id externo se busca "en este hogar". |
| Acceso delegado (OAuth, módulo 90) | Una view acepta tokens de aplicaciones solo si lo declara: `AceptaOAuth` y `scopes_por_accion` (lo que no aparece no se delega). El adapter de autenticación deja una `Delegacion` (`core/domain/vo/delegacion.py`) en `request.auth`; `actor_de` limita el rol del Actor al techo de sus scopes (`Actor.limitado_a`): scope Y rol, la intersección. Ningún scope llega a ADMIN. Cuenta, autenticación y backoffice no aceptan tokens OAuth. |
| Tarea de Celery | Un archivo por tarea en `infrastructure/tasks/`, con `name="<app>.tasks.<función>"`. `apps.ready()` importa los receivers y las tareas. |
| Tarea de django.tasks | Un archivo en `infrastructure/tasks/` con `@ruta_estable("<app>.tasks")` debajo de `@task` (la ruta es su identidad en la cola) y un `<app>/tasks.py` que la reexporta. El publicador la encola con `import_string(RUTA).enqueue(...)`; las de Celery, por su nombre (`current_app.tasks[NOMBRE]`), sin importar `tasks/` (está por encima). |
| Excepción de un adapter | La que no es del dominio (`TransitorioIAException`, `CircuitoAbiertoException`, `SinTransaccionException`) vive en un archivo junto a su adapter, con el mismo sufijo. |
| Entre apps | Una app pide a otra con el contenedor de la otra, desde su `infrastructure/finanzas/` (*anti-corruption layer*), que traduce a sus propios tipos (un ticket habla de su `total`; finanzas, de un `importe` negativo). Escribir en las tablas de otra app con el ORM está prohibido; leerlas, con sus modelos o sus query services, no. |
| Social login (módulo 91) | Gastos es el cliente (Relying Party) y el patrón es BFF: Django hace la ida y la vuelta, canjea el code con su secreto y valida el ID token; los tokens del proveedor no salen del *adapter*. Port `IProveedorIdentidad` (un *adapter* por proveedor) que devuelve un `PerfilExterno` ya comprobado; la identidad es (proveedor, `sub`), nunca el email. `CompletarLoginSocialUseCase` decide (dominio: `decidir_entrada`, `decidir_vinculo`) e `IniciarSesionUseCase` emite los tokens de la SPA: es el único sitio donde se emiten, también tras la contraseña. |
| Sesiones, MFA y *step-up* (módulo 92) | `IniciarSesionUseCase` es el único sitio donde se abre una sesión (SPA o *authorization server*, contraseña, proveedor o passkey): con MFA activo y un primer factor que no basta, devuelve un `SegundoFactorPendienteOutputDTO` (clave en una cookie HttpOnly o en la sesión de Django del AS) y la sesión la abre `CompletarSegundoFactorUseCase`; los dos terminan en `AperturaDeSesion` (`application/shared/`). Cada sesión tiene nombre (`sid` en el refresh y el access de simplejwt; en la sesión de Django del AS) y una fila `Sesion` con sus factores, su `autenticada` (el auth_time), su caducidad y el jti de su refresh vigente: solo ese la renueva, y uno ya rotado que vuelve la cierra (detección de reutilización, RFC 9700); la base de datos no guarda ningún refresh token. Las acciones sensibles llevan `AutenticacionReciente` (*step-up*, RFC 9470); `ReautenticarUseCase` renueva el momento sin tokens nuevos. El secreto TOTP se cifra en el repositorio (MultiFernet, `MFA_CLAVES`); los códigos de recuperación, con PBKDF2 (selector + verificador). |
| Actor de un proceso | `Actor.sistema(en_nombre_de=usuario_id)` en tareas que trabajan para alguien (lo creado queda a su nombre); `Actor.soporte(usuario_id)` en el backoffice (rol ADMIN en cualquier hogar, auditado con su usuario). |
| Escrituras sin use case | Movimientos, presupuestos, categorías y membresías tienen eventos que solo publica el use case. Sus receivers de `post_save`/`post_delete` son una alarma (`vigilar`, en `core/infrastructure/signals/red_de_seguridad.py`): lanzan `EscrituraSinCasoDeUsoException` con `EXIGIR_CASOS_DE_USO=True` (dev, tests, E2E) y en producción dejan un error en el log. El repositorio marca lo que guarda (`publicados_por_caso_de_uso`) y lo que escribe en bloque va dentro de `en_un_caso_de_uso()`; los datos de partida de un test (factories), dentro de `escrituras_directas()`. |
| Cascadas | Lo que borra la base de datos por cascada (borrar un hogar) no pasa por los use cases de los hijos: los receivers lo detectan con el argumento `origin` de `post_delete` (`es_cascada`) y publican solo lo imprescindible (tombstones). |
| Agente (Parte 7) | El *agent loop* (`asistente/application/agent/agente.py`) solo conoce `ILLM` y sus *tools*; cada *tool* (`application/tools/`, una clase por archivo con su modelo de argumentos de pydantic) recibe sus *ports* por el constructor y el `ContextoPregunta` (usuario, hogar, `Actor` limitado a LECTOR, el día de hoy en la zona del hogar), que construye el *adapter* de entrada con la sesión: ninguna *tool* tiene un argumento `hogar_id`. Los errores previstos (`ToolException`, `DominioException`) vuelven al modelo como resultado; los demás, al *log* |
| Prompts (Parte 7) | Los *prompts* son código (`asistente/application/prompts/`, módulo 96): una `PlantillaDePrompt` con nombre, versión y huella, rellenada de forma estricta (un hueco sin valor es un error); `versiones.py` registra la huella de cada versión publicada y un test impide cambiar el texto sin publicar una versión nueva; un *golden file* con el *prompt* de un día concreto. Todo lo que depende de la fecha sale del `ContextoPregunta`, no del reloj del servidor. La versión viaja en la línea de *log* de cada pregunta. El historial que viaja en cada llamada lo decide `ventana.py` (presupuesto de contexto) |
| Seguridad del agente (Parte 7) | Lo que no ha escrito la persona es de terceros (módulo 102): las *tools* que lo traen (tickets, conceptos de extractos, comercios, filas del SQL) lo declaran con `lee_terceros = True`, y su resultado (o su error) pasa por el `Vigilante` (`application/seguridad/`), la política sobre un `IDetectorDeInyeccion` (`DetectorPromptGuard` en `infrastructure/llm/`): si parece una inyección, el modelo no lo lee y la persona ve un aviso; si el clasificador no está disponible, pasa (*fail open*), y si falla por el texto (un 4xx, demasiado largo), se retira (*fail closed*). Desde que la conversación tiene terceros (`Procedencia`, guardada en `Conversacion.con_terceros`; un adjunto, desde el principio), las *tools* con `persiste = True` (recordar, olvidar) se niegan. Todo lo que escribe el modelo (la respuesta, sus preguntas de seguimiento, el título de un gráfico, el concepto de una propuesta) sale sin imágenes, enlaces, URLs ni HTML (`application/seguridad/sanear_respuesta.py`, con un parser CommonMark): los enlaces los pone el código, nunca el texto del modelo. Cada barrera, en `tests/seguridad/` con un modelo falso que obedece todo (`ataques.yaml`) |
| MCP (Parte 7) | El servidor MCP (`asistente/infrastructure/api/mcp/`, módulo 104) es un *adapter* de entrada como la API REST: saca la persona del token (emitido para `/api/mcp` con `resource`, RFC 8707, y comprobado exacto en `oauth/infrastructure/api/authentication/token_de_recurso.py`), monta el `ContextoPregunta` con el rol ∩ el techo del *scope* ∩ LECTOR y ejecuta las mismas *tools* de consulta. `config/asgi.py` le pasa `/api/mcp` y su Protected Resource Metadata; como no pasa por el `ASGIHandler` de Django, `AplicacionMCP` pone lo que este haría (un `ThreadSensitiveContext` por petición y `close_old_connections`). El cliente (`asistente/infrastructure/mcp/`) es un *adapter* de salida detrás de `IServidorMCP`: solo las *tools* aprobadas con su huella, `ToolRemota` con `lee_terceros` y `envia_fuera` (en una conversación con terceros no se llama) y el token de cada servidor (nunca el de la persona). |
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
| usuarios | registro, recuperación, contraseña, social login (módulo 91), sesiones, MFA y passkeys (módulo 92) | — | `usuarios.models`, su contenedor (`iniciar_sesion`, `completar_segundo_factor`, `obtener_factores`…), `JWTConSesion`, `AutenticacionReciente` y la sesión de Django del *authorization server* (`api/sessions/`) |
| tickets | tickets | `IGastos` → finanzas | `tickets_signals`, `TicketQueryServiceORM` (los atascados) |
| importaciones | importaciones y sus filas | `IMovimientos` → finanzas | `importaciones_signals` |
| informes | informes mensuales | lee el dashboard y los movimientos del mes (query services de finanzas) | `informes_signals` |
| notificaciones | notificaciones | `IDestinatarios` (usuarios y membresías, por sus modelos) | — (escucha las signals de las demás) |
| eventos | el outbox | — | `IOutbox` (lo usan los publicadores de finanzas y hogares) |
| backoffice | nada propio | los use cases de tickets, importaciones y finanzas, con `Actor.soporte` | — |
| oauth | clientes registrados (el *authorization server* del módulo 90, sobre django-oauth-toolkit) | — | la autenticación OAuth de la API y `AceptaOAuth` (las views de finanzas y hogares la usan) |
| asistente | conversaciones, carpetas, propuestas y gráficos fijados (módulo 97); el libro de cuentas (lo gastado por pregunta y modelo) y el plan de cada hogar (módulo 98); los recuerdos de cada persona y el resumen de cada conversación (módulo 99); el índice de la ayuda (módulo 100), que se reconstruye desde los `.md`. Sus *tools* solo leen, con un `Actor` limitado a LECTOR; lo que cambia datos del hogar es una propuesta que la persona confirma, y la ejecuta el *use case* de la app dueña con SU `Actor` | `IConsultasDeFinanzas`, `IExportadorDeMovimientos`, `IEjecutorDePropuestas` → finanzas; `IMembresias` → hogares; `ITickets`, `ILectorDeAdjuntos` → tickets | — |

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
│   ├── services/         interpretacion.py (interpretar: de un mensaje a un evento), medias_por_dia.py, ahorro.py
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
│   │   ├── app.py        crear_app(): el router principal (monta cada versión con su prefijo y los handlers)
│   │   ├── dependencies/ usuario_actual.py (el JWT de Django), hogar_permitido.py (Hogar: 404 si no eres miembro)
│   │   ├── exceptions/   mes_mal_formado_handler.py (MesMalFormadoException → 422)
│   │   ├── v1/
│   │   │   ├── routers/  tendencia_router.py → tendencia() (un endpoint por archivo; y salud, dias_semana…)
│   │   │   ├── schemas/  tendencia_schema.py → Tendencia (el contrato OpenAPI; un schema por archivo)
│   │   │   ├── router.py el APIRouter de la v1: reúne los de routers/ (el urls.py de Django)
│   │   │   └── parametros.py  Meses (query param con sus límites)
│   │   └── v2/           router.py, routers/tendencia_router.py, schemas/ (TendenciaConTasa…): convive con la v1
│   ├── database/
│   │   ├── models/       movimiento_model.py → MovimientoModel (SQLAlchemy 2), base.py → Base
│   │   ├── repositories/ movimiento_command_repository_sql.py → MovimientoCommandRepositorySQL
│   │   │                 movimiento_query_service_sql.py → MovimientoQueryServiceSQL
│   │   ├── metadata.py   puerta de entrada de los modelos (la leen Alembic y el test de migraciones)
│   │   └── unidad_de_trabajo_sql.py, sesiones.py, guardado.py (DataError → EventoInvalidoException), conexion.py
│   ├── consumer/         consumidor_kafka.py (el bucle de Kafka) y reintentos_kafka.py (los aparcados): de entrada
│   ├── cli/              reconstruir_cli.py (adapter de entrada: línea de comandos)
│   ├── messaging/        aparcados_kafka.py → AparcadosKafka, grupo_kafka.py → GrupoKafka (adapters de salida)
│   ├── metrics/          retraso_consumidor.py (el gauge del retraso, que publica la API)
│   ├── telemetry/        telemetria.py, trazas_otel.py → TrazasOTel, traza_otel.py → TrazaOTel
│   ├── clock/            reloj_sistema.py → RelojSistema
│   └── container.py      composition root: una función por use case (y las dependencias de FastAPI)
├── ajustes.py            configuración (pydantic-settings). Solo la leen el container y la infraestructura
└── api.py, consumidor.py, reconstruir.py, reintentar.py   puntos de entrada (uvicorn, python -m)
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
2. Capas, de arriba abajo: puntos de entrada (`api | consumidor | reconstruir | reintentar`) → `infrastructure.api |
   consumer | cli` → `infrastructure.container` → `infrastructure.telemetry` → `infrastructure.database | messaging |
   metrics | clock` → `application` → `domain`.
3. Los paquetes de los *use cases* son independientes entre sí: lo que comparten va en `application/shared` o en
   `ports`.

El CI ejecuta `tests/domain`, `tests/application` y `tests/fakes` sin PostgreSQL ni Kafka (con `DATABASE_URL` y
`KAFKA_BOOTSTRAP_SERVERS` apuntando a puertos cerrados) y después `tests/infrastructure` con los dos.
