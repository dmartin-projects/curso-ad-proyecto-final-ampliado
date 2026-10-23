import { createHmac } from 'node:crypto';

import { expect, Page } from '@playwright/test';

export const DEMO = { email: 'demo@example.com', password: 'demo12345-demo' };
export const SOPORTE = { email: 'soporte@example.com', password: 'soporte12345' };
/** Módulo 92, ejercicio 1: el personal tiene MFA; este es su secreto TOTP (preparar_e2e, solo E2E). */
export const SECRETO_SOPORTE = 'JBSWY3DPEHPK3PXP';

/** RFC 6238: HMAC-SHA1(secreto, paso de 30 s), truncado a 6 cifras. `desfase` en segundos (módulo 92). */
export function totp(secreto: string, desfase = 0): string {
  const alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  const bits = [...secreto.replace(/=+$/, '')]
    .map((c) => alfabeto.indexOf(c).toString(2).padStart(5, '0'))
    .join('');
  const clave = Buffer.from(bits.match(/.{8}/g)!.map((b) => parseInt(b, 2)));
  const paso = Buffer.alloc(8);
  paso.writeBigUInt64BE(BigInt(Math.floor((Date.now() / 1000 + desfase) / 30)));
  const hmac = createHmac('sha1', clave).update(paso).digest();
  const desde = hmac[hmac.length - 1] & 0x0f;
  return String((hmac.readUInt32BE(desde) & 0x7fffffff) % 1_000_000).padStart(6, '0');
}

/**
 * Login por la interfaz en cada test. No sirve guardar la sesión con `storageState`: el refresh token ROTA
 * en cada uso (ROTATE_REFRESH_TOKENS, módulo 35) y la cookie guardada ya no valdría tras el primer test (desde
 * el módulo 92, además, un refresh ya rotado que vuelve cierra su sesión: detección de reutilización).
 */
export async function entrar(
  page: Page,
  usuario = DEMO,
  estadisticas = simularEstadisticas,
  secreto?: string,
) {
  await estadisticas(page);
  await page.goto('/login');
  await page.getByLabel('Email').fill(usuario.email);
  await page.getByLabel('Contraseña').fill(usuario.password);
  await page.getByRole('button', { name: 'Entrar', exact: true }).click(); // (no «Entrar con una passkey»)
  if (secreto) {
    // Módulo 92: la cuenta tiene MFA. El segundo paso, con el código que daría su app
    await expect(page).toHaveURL(/\/login\/segundo-factor/);
    await page.getByLabel('Código').fill(totp(secreto));
    await page.getByRole('button', { name: 'Verificar' }).click();
  }
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
