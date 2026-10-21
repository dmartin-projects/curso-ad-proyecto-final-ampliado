import { expect, Page } from '@playwright/test';

export const DEMO = { email: 'demo@example.com', password: 'demo12345-demo' };
export const SOPORTE = { email: 'soporte@example.com', password: 'soporte12345' };

/**
 * Login por la interfaz en cada test. No sirve guardar la sesión con `storageState`: el refresh token ROTA
 * en cada uso (ROTATE_REFRESH_TOKENS + BLACKLIST_AFTER_ROTATION, módulo 35) y la cookie guardada quedaría
 * en la lista negra tras el primer test.
 */
export async function entrar(page: Page, usuario = DEMO, estadisticas = simularEstadisticas) {
  await estadisticas(page);
  await page.goto('/login');
  await page.getByLabel('Email').fill(usuario.email);
  await page.getByLabel('Contraseña').fill(usuario.password);
  await page.getByRole('button', { name: 'Entrar' }).click();
  await expect(page).not.toHaveURL(/login/);
}

/** Falla el test si la página escribe errores en la consola (salvo el 401 esperado del primer refresh). */
export function vigilarConsola(page: Page) {
  const errores: string[] = [];
  page.on('pageerror', (e) => errores.push(e.message));
  page.on('console', (m) => {
    if (m.type() === 'error' && !m.text().includes('401')) errores.push(m.text());
  });
  return () => expect(errores, errores.join('\n')).toEqual([]);
}

/**
 * El servicio de estadísticas (módulo 85) no se arranca en estos E2E, que prueban la aplicación de Django:
 * su respuesta se simula en el navegador. El servicio tiene sus propios tests (estadisticas/tests) y el
 * recorrido contra la producción levantada en local lo prueba de verdad, con Kafka.
 */
export async function simularEstadisticas(page: Page) {
  await page.route('**/estadisticas/v1/**', (r) =>
    r.fulfill({
      json: {
        hogar_id: 1,
        ultimo_evento: '2026-10-21T22:43:52Z',
        desde: '2026-05-01',
        hasta: '2026-10-21',
        dias: ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'].map(
          (nombre, i) => ({ dia: i + 1, nombre, gasto_medio: String(10 + i) }),
        ),
      },
    }),
  );
}

/** El servicio de estadísticas caído: Caddy responde 502. */
export async function estadisticasCaidas(page: Page) {
  await page.route('**/estadisticas/v1/**', (r) => r.fulfill({ status: 502, body: 'Bad Gateway' }));
}
