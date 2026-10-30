# Módulo 101: text-to-SQL con un rol de PostgreSQL que solo puede LEER lo de UN hogar.
"""Lo que el modelo escriba no se ejecuta con el usuario de la aplicación, sino con `gastos_asistente_sql`:

- un rol aparte, con su propia conexión (ASISTENTE_SQL_*): nunca un SET ROLE sobre la conexión de la app (desde una
  consulta, `set_config('role', 'gastos', true)` volvería a ser la app);
- SELECT solo sobre las columnas que necesita (ni IBAN, ni notas, ni quién creó qué) y ningún permiso de escritura;
- Row Level Security en las tablas de finanzas, solo para ese rol: ve las filas del hogar que diga
  `asistente_sql.hogar()`, que lee una tabla que ese rol NO puede escribir, por el pid de su conexión. Un hogar
  guardado en una variable (`set_config('gastos.hogar_id', …)`) lo podría cambiar la propia consulta;
- unas vistas con nombres y columnas pensados para el modelo (`movimientos`, `categorias`…), que se ejecutan con los
  permisos de quien consulta (security_invoker): las reglas de arriba se aplican también a través de ellas.

La aplicación (el dueño de las tablas) no se ve afectada: el dueño se salta la RLS salvo con FORCE, que no se usa.
"""

from django.db import migrations

ROL = "gastos_asistente_sql"
TABLAS = ["finanzas_movimiento", "finanzas_categoria", "finanzas_cuenta", "finanzas_presupuesto", "finanzas_comercio"]

ADELANTE = f"""
DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{ROL}') THEN
        CREATE ROLE {ROL} NOLOGIN;  -- la contraseña y el LOGIN, con manage.py preparar_rol_sql (no en una migración)
    END IF;
END $$;

CREATE SCHEMA asistente_sql;

-- Qué hogar ve cada conexión del rol. La escribe la app (con su usuario) antes de la consulta y la borra después
CREATE TABLE asistente_sql.contexto (pid integer PRIMARY KEY, hogar_id bigint NOT NULL, desde timestamptz NOT NULL DEFAULT now());
REVOKE ALL ON asistente_sql.contexto FROM PUBLIC;

CREATE FUNCTION asistente_sql.hogar() RETURNS bigint
    LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog, pg_temp
    AS $f$ SELECT hogar_id FROM asistente_sql.contexto WHERE pid = pg_backend_pid() $f$;
REVOKE ALL ON FUNCTION asistente_sql.hogar() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION asistente_sql.hogar() TO {ROL};

-- Row Level Security, solo para el rol del asistente (sin contexto, hogar() es NULL: no ve nada)
ALTER TABLE finanzas_movimiento ENABLE ROW LEVEL SECURITY;
ALTER TABLE finanzas_categoria ENABLE ROW LEVEL SECURITY;
ALTER TABLE finanzas_cuenta ENABLE ROW LEVEL SECURITY;
ALTER TABLE finanzas_presupuesto ENABLE ROW LEVEL SECURITY;
ALTER TABLE finanzas_comercio ENABLE ROW LEVEL SECURITY;
CREATE POLICY asistente_sql_hogar ON finanzas_movimiento FOR SELECT TO {ROL} USING (hogar_id = asistente_sql.hogar());
CREATE POLICY asistente_sql_hogar ON finanzas_categoria FOR SELECT TO {ROL} USING (hogar_id = asistente_sql.hogar());
CREATE POLICY asistente_sql_hogar ON finanzas_cuenta FOR SELECT TO {ROL} USING (hogar_id = asistente_sql.hogar());
CREATE POLICY asistente_sql_hogar ON finanzas_presupuesto FOR SELECT TO {ROL} USING (hogar_id = asistente_sql.hogar());
-- los comercios son de todos los hogares: el rol solo ve los que aparecen en los movimientos del suyo
CREATE POLICY asistente_sql_hogar ON finanzas_comercio FOR SELECT TO {ROL}
    USING (EXISTS (SELECT 1 FROM finanzas_movimiento m WHERE m.comercio_id = finanzas_comercio.id));

-- Solo las columnas que hacen falta
GRANT USAGE ON SCHEMA public, asistente_sql TO {ROL};
GRANT SELECT (id, hogar_id, fecha, importe, concepto, categoria_id, cuenta_id, comercio_id, etiquetas)
    ON finanzas_movimiento TO {ROL};
GRANT SELECT (id, hogar_id, nombre, padre_id, es_ingreso) ON finanzas_categoria TO {ROL};
GRANT SELECT (id, hogar_id, nombre, tipo, activa) ON finanzas_cuenta TO {ROL};
GRANT SELECT (id, hogar_id, categoria_id, mes, importe) ON finanzas_presupuesto TO {ROL};
GRANT SELECT (id, nombre) ON finanzas_comercio TO {ROL};

-- Las vistas que ve el modelo (y que describe la tool consultar_sql)
CREATE VIEW asistente_sql.movimientos WITH (security_invoker = true) AS
    SELECT m.fecha, m.importe, m.concepto, c.nombre AS categoria, p.nombre AS categoria_padre,
           cu.nombre AS cuenta, co.nombre AS comercio, m.etiquetas
    FROM finanzas_movimiento m
    JOIN finanzas_cuenta cu ON cu.id = m.cuenta_id
    LEFT JOIN finanzas_categoria c ON c.id = m.categoria_id
    LEFT JOIN finanzas_categoria p ON p.id = c.padre_id
    LEFT JOIN finanzas_comercio co ON co.id = m.comercio_id;
CREATE VIEW asistente_sql.categorias WITH (security_invoker = true) AS
    SELECT c.nombre, p.nombre AS padre, c.es_ingreso
    FROM finanzas_categoria c LEFT JOIN finanzas_categoria p ON p.id = c.padre_id;
CREATE VIEW asistente_sql.cuentas WITH (security_invoker = true) AS
    SELECT nombre, tipo, activa FROM finanzas_cuenta;
CREATE VIEW asistente_sql.presupuestos WITH (security_invoker = true) AS
    SELECT pr.mes, c.nombre AS categoria, pr.importe
    FROM finanzas_presupuesto pr JOIN finanzas_categoria c ON c.id = pr.categoria_id;
GRANT SELECT ON asistente_sql.movimientos, asistente_sql.categorias, asistente_sql.cuentas, asistente_sql.presupuestos
    TO {ROL};
ALTER ROLE {ROL} SET search_path = asistente_sql;
"""

ATRAS = f"""
DROP SCHEMA asistente_sql CASCADE;
{"".join(f"DROP POLICY IF EXISTS asistente_sql_hogar ON {t}; ALTER TABLE {t} DISABLE ROW LEVEL SECURITY; " for t in TABLAS)}
REVOKE ALL ON {", ".join(TABLAS)} FROM {ROL};
REVOKE USAGE ON SCHEMA public FROM {ROL};
"""


class Migration(migrations.Migration):
    dependencies = [
        ("asistente", "0004_ayuda"),
        ("finanzas", "0002_categorias_hogares_existentes"),
    ]

    operations = [migrations.RunSQL(ADELANTE, ATRAS)]
