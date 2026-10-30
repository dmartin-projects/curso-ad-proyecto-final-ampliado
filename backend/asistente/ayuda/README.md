# La ayuda de Gastos (módulo 100)

Lo que el asistente consulta con la *tool* `buscar_ayuda` para contestar "¿cómo se hace…?" sobre la app. Es
documentación, no código: la escribe quien sabe cómo funciona la app, en castellano, y se revisa en el *pull request*
como cualquier cambio.

- Un archivo por tema, con su cabecera (`titulo`, `actualizado`) y secciones `##`: cada sección es un trozo que se
  indexa por separado (un trozo, una respuesta). Mejor secciones cortas con un título que diga de qué van.
- Al cambiar un archivo, `manage.py indexar_ayuda` vuelve a calcular solo lo que ha cambiado (la huella de cada trozo).
- Lo que no esté aquí, el asistente no lo sabe: dirá que no lo sabe (y eso es mejor que inventarlo).
