import { createHash, randomBytes } from 'node:crypto';

import { expect, Page, test } from '@playwright/test';

import { DEMO, entrar } from './ayuda';

/**
 * Módulo 90: Gastos como authorization server. Una aplicación (gastos-cli) pide acceso y el usuario entra y consiente
 * en las páginas del propio Gastos (Django, no la SPA). La vuelta a la app (http://127.0.0.1:<puerto>/callback, su
 * servidor de loopback) la intercepta Playwright.
 */
const VUELTA = 'http://127.0.0.1:53682/callback';

function pkce() {
  const verifier = randomBytes(48).toString('base64url');
  return { verifier, challenge: createHash('sha256').update(verifier).digest('base64url') };
}

async function pedirAcceso(page: Page, challenge: string) {
  let vuelta: URL | undefined;
  await page.route('http://127.0.0.1:53682/**', (r) => {
    vuelta = new URL(r.request().url());
    return r.fulfill({ body: 'Listo. Vuelve a la terminal.' });
  });
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: 'gastos-cli',
    redirect_uri: VUELTA,
    scope: 'openid email gastos:leer',
    state: 'estado-e2e',
    nonce: 'nonce-e2e',
    code_challenge: challenge,
    code_challenge_method: 'S256',
  });
  await page.goto(`/api/oauth/authorize/?${params}`);
  await expect(page.getByRole('heading', { name: 'Entrar en Gastos' })).toBeVisible();
  await page.getByLabel('Correo electrónico').fill(DEMO.email); // "Email", con la traducción de Django
  await page.getByLabel('Contraseña').fill(DEMO.password);
  await page.getByRole('button', { name: 'Entrar' }).click();
  await expect(
    page.getByRole('heading', { name: '«Gastos CLI» quiere acceder a tu cuenta' }),
  ).toBeVisible();
  await expect(
    page.getByText('Ver los movimientos, las cuentas y el resumen de tus hogares'),
  ).toBeVisible();
  return () => vuelta;
}

test('una aplicación pide acceso: login, consentimiento, code y token', async ({
  page,
  request,
}) => {
  const { verifier, challenge } = pkce();
  const vuelta = await pedirAcceso(page, challenge);
  await page.getByRole('button', { name: 'Permitir' }).click();
  await expect.poll(() => vuelta()?.searchParams.get('state')).toBe('estado-e2e');
  expect(vuelta()!.searchParams.get('iss')).toBe('http://localhost:4200/api/oauth');

  const respuesta = await request.post('/api/oauth/token/', {
    form: {
      grant_type: 'authorization_code',
      code: vuelta()!.searchParams.get('code')!,
      redirect_uri: VUELTA,
      client_id: 'gastos-cli',
      code_verifier: verifier,
    },
  });
  const tokens = await respuesta.json();
  expect(tokens.access_token).toMatch(/^gst_at_/);
  const hogares = await request.get('/api/v1/hogares/', {
    headers: { Authorization: `Bearer ${tokens.access_token}` },
  });
  expect(hogares.ok()).toBeTruthy();
  // la cuenta no se gestiona con un token de aplicación
  const yo = await request.get('/api/v1/auth/me/', {
    headers: { Authorization: `Bearer ${tokens.access_token}` },
  });
  expect(yo.status()).toBe(401);
});

test('si el usuario cancela, la aplicación recibe access_denied', async ({ page }) => {
  const vuelta = await pedirAcceso(page, pkce().challenge);
  await page.getByRole('button', { name: 'Cancelar' }).click();
  await expect.poll(() => vuelta()?.searchParams.get('error')).toBe('access_denied');
  expect(vuelta()!.searchParams.has('code')).toBe(false);
});

// Ejercicio 1: el usuario ve a qué aplicaciones ha dado acceso y se lo retira desde la app
test('aplicaciones conectadas: retirar el acceso corta el token al momento', async ({
  page,
  request,
}) => {
  const { verifier, challenge } = pkce();
  const vuelta = await pedirAcceso(page, challenge);
  await page.getByRole('button', { name: 'Permitir' }).click();
  await expect.poll(() => vuelta()?.searchParams.get('code')).toBeTruthy();
  const tokens = await (
    await request.post('/api/oauth/token/', {
      form: {
        grant_type: 'authorization_code',
        code: vuelta()!.searchParams.get('code')!,
        redirect_uri: VUELTA,
        client_id: 'gastos-cli',
        code_verifier: verifier,
      },
    })
  ).json();
  const conToken = { headers: { Authorization: `Bearer ${tokens.access_token}` } };
  expect((await request.get('/api/v1/hogares/', conToken)).status()).toBe(200);

  await entrar(page);
  await page.getByRole('button', { name: 'Mi cuenta' }).click();
  await page.getByRole('menuitem', { name: 'Aplicaciones conectadas' }).click();
  const fila = page.getByRole('listitem').filter({ hasText: 'Gastos CLI' });
  await expect(fila).toContainText('Ver los movimientos, las cuentas y el resumen de tus hogares');
  await fila.getByRole('button', { name: 'Retirar acceso' }).click();
  await page.getByRole('alertdialog').getByRole('button', { name: 'Retirar acceso' }).click();
  await expect(page.getByText('Ninguna aplicación tiene acceso a tu cuenta.')).toBeVisible();

  expect((await request.get('/api/v1/hogares/', conToken)).status()).toBe(401);
});
