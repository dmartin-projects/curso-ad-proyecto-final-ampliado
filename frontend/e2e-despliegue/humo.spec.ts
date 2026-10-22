import { expect, test } from '@playwright/test';

/**
 * Lo que solo se puede comprobar con el entorno de verdad (módulo 86, ejercicio 1): el rewrite de Vercel,
 * la cookie de refresh a través de él, Caddy con su secreto y el WebSocket DIRECTO a la API.
 * Usuario propio de la prueba (HUMO_EMAIL), sin datos de nadie: en staging, créalo una vez.
 */
test('login, recargar, la API y el WebSocket en el entorno desplegado', async ({
  page,
  context,
}) => {
  const { HUMO_EMAIL, HUMO_PASSWORD, VERCEL_AUTOMATION_BYPASS_SECRET: bypass } = process.env;
  test.skip(!HUMO_EMAIL || !HUMO_PASSWORD, 'Faltan HUMO_EMAIL y HUMO_PASSWORD');

  // Las previews y staging están protegidas (Vercel Authentication): una cookie de paso, una sola vez.
  // Por la URL y no como cabecera de todas las peticiones: así el secreto no viaja también a la API.
  if (bypass) {
    await page.goto(`/?x-vercel-protection-bypass=${bypass}&x-vercel-set-bypass-cookie=true`);
  }

  const conectado = new Promise<string>((listo) =>
    page.on('websocket', (ws) =>
      ws.on('framereceived', ({ payload }) => {
        if (String(payload).includes('"conectado"')) listo(ws.url());
      }),
    ),
  );

  await page.goto('/login');
  await page.getByLabel('Email').fill(HUMO_EMAIL!);
  await page.getByLabel('Contraseña').fill(HUMO_PASSWORD!);
  await page.getByRole('button', { name: 'Entrar' }).click();
  await expect(page).not.toHaveURL(/login/);

  const web = new URL(page.url()).hostname;
  const refresh = (await context.cookies()).find((c) => c.name === 'refresh');
  expect(refresh, 'la cookie de refresh llega a través del rewrite').toMatchObject({
    domain: web,
    path: '/api/v1/auth/',
    httpOnly: true,
    secure: true,
  });

  const socket = new URL(await conectado);
  expect(socket.hostname, 'el WebSocket va directo a la API, no a Vercel').not.toBe(web);

  await page.reload(); // la sesión vuelve solo con la cookie
  await expect(page).not.toHaveURL(/login/);
  await expect(page.getByRole('heading').first()).toBeVisible();
});
