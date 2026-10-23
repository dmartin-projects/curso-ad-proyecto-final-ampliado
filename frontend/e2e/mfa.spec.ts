import { Browser, expect, Page, test } from '@playwright/test';

import { simularEstadisticas, totp } from './ayuda';

/**
 * Módulo 92: la verificación en dos pasos, las passkeys, el step-up y las sesiones, en un navegador de verdad.
 * - TOTP: el código lo calcula el test con el secreto que enseña la pantalla (RFC 6238), como la app del móvil.
 * - Passkeys: el autenticador virtual de Chromium (CDP WebAuthn), con huella "simulada" (isUserVerified).
 */
const cuenta = (nombre: string) => ({
  email: `${nombre}@example.com`,
  password: `${nombre}-clave-e2e`,
});

async function conContrasena(page: Page, usuario: { email: string; password: string }) {
  await simularEstadisticas(page);
  await page.goto('/login');
  await page.getByLabel('Email').fill(usuario.email);
  await page.getByLabel('Contraseña').fill(usuario.password);
  await page.getByRole('button', { name: 'Entrar', exact: true }).click();
}

async function menu(page: Page, opcion: string) {
  await page.getByRole('button', { name: 'Mi cuenta' }).click();
  await page.getByRole('menuitem', { name: opcion }).click();
}

async function salir(page: Page) {
  await page.getByRole('button', { name: 'Mi cuenta' }).click();
  await page.getByRole('menuitem', { name: 'Cerrar sesión' }).click();
  await expect(page).toHaveURL(/\/login/);
}

test('activa la verificación en dos pasos y entra con el código de la app y con uno de recuperación', async ({
  page,
}) => {
  const ana = cuenta('mfa');
  await conContrasena(page, ana);
  await expect(page).toHaveURL(/\/hogares/);
  await menu(page, 'Seguridad');
  await page.getByRole('button', { name: 'Activar' }).click();
  await expect(
    page.getByRole('img', { name: 'Código QR para tu app de autenticación' }),
  ).toBeVisible();
  const secreto = (await page.getByTestId('secreto').textContent())!.trim();
  await page.getByLabel('Código de 6 cifras').fill(totp(secreto));
  await page.getByRole('button', { name: 'Activar' }).click();
  const codigos = page.getByRole('list', { name: 'Códigos de recuperación' }).getByRole('listitem');
  await expect(codigos).toHaveCount(10);
  const recuperacion = (await codigos.first().textContent())!.trim();
  await page.getByRole('button', { name: 'Ya los he guardado' }).click();
  await expect(page.getByText('Te quedan 10 códigos de recuperación.')).toBeVisible();
  await salir(page);

  // La contraseña ya no basta: el segundo paso, con el código de la app (el del paso siguiente: uno nuevo)
  await conContrasena(page, ana);
  await expect(page).toHaveURL(/\/login\/segundo-factor/);
  await page.getByLabel('Código').fill(totp(secreto, 30));
  await page.getByRole('button', { name: 'Verificar' }).click();
  await expect(page).toHaveURL(/\/hogares/);
  await salir(page);

  // Sin el móvil: un código de recuperación (una vez)
  await conContrasena(page, ana);
  await page.getByRole('button', { name: /código de recuperación/ }).click();
  await page.getByLabel('Código de recuperación').fill(recuperacion);
  await page.getByRole('button', { name: 'Verificar' }).click();
  await expect(page).toHaveURL(/\/hogares/);
  await menu(page, 'Seguridad');
  await expect(page.getByText('Te quedan 9 códigos de recuperación.')).toBeVisible();
});

test('añade una passkey y entra con ella, sin contraseña', async ({ page }) => {
  // El autenticador de la plataforma, virtual: guarda passkeys (resident keys) y "verifica" al usuario
  const cdp = await page.context().newCDPSession(page);
  await cdp.send('WebAuthn.enable', { enableUI: false });
  const { authenticatorId } = await cdp.send('WebAuthn.addVirtualAuthenticator', {
    options: {
      protocol: 'ctap2',
      transport: 'internal',
      hasResidentKey: true,
      hasUserVerification: true,
      isUserVerified: true,
      automaticPresenceSimulation: true,
    },
  });

  await conContrasena(page, cuenta('passkey'));
  await expect(page).toHaveURL(/\/hogares/);
  await menu(page, 'Seguridad');
  await page.getByRole('button', { name: 'Añadir una passkey' }).click();
  await expect(page.getByText('Passkey de Chrome en Windows')).toBeVisible(); // el user agent de «Desktop Chrome»
  const { credentials } = await cdp.send('WebAuthn.getCredentials', { authenticatorId });
  expect(credentials).toHaveLength(1);
  expect(credentials[0].rpId).toBe('localhost'); // atada al dominio de la app
  expect(credentials[0].isResidentCredential).toBe(true); // discoverable: sin escribir el email
  await salir(page);

  // De vuelta en el login, la SPA pide las passkeys para el autorrelleno del email (conditional UI). En un navegador
  // de verdad, la persona la elige en el desplegable; el autenticador virtual (presencia automática) responde solo
  await expect(page).toHaveURL(/\/hogares/); // ni email ni contraseña
  await menu(page, 'Sesiones');
  await expect(page.getByText(/con passkey/)).toHaveCount(1); // la sesión: un solo factor, y multifactor
  const despues = await cdp.send('WebAuthn.getCredentials', { authenticatorId });
  expect(despues.credentials[0].signCount).toBeGreaterThan(0); // el contador que comprueba el backend
});

test('una acción sensible pide confirmar quién eres y luego se hace', async ({ page, request }) => {
  await conContrasena(page, cuenta('stepup'));
  await expect(page).toHaveURL(/\/hogares/);
  await menu(page, 'Seguridad');
  await request.post('http://localhost:8000/e2e/sesiones/envejecer'); // la sesión se abrió "hace una hora"
  await page.getByRole('button', { name: 'Activar' }).click();
  const dialogo = page.getByRole('dialog', { name: 'Confirma que eres tú' });
  await dialogo.getByLabel('Contraseña').fill('mala');
  await dialogo.getByRole('button', { name: 'Confirmar' }).click();
  await expect(dialogo.getByRole('alert')).toContainText('La contraseña no es correcta.');
  await dialogo.getByLabel('Contraseña').fill(cuenta('stepup').password);
  await dialogo.getByRole('button', { name: 'Confirmar' }).click();
  // La petición se repite sola: sin volver a pulsar "Activar"
  await expect(
    page.getByRole('img', { name: 'Código QR para tu app de autenticación' }),
  ).toBeVisible();
});

async function otroNavegador(browser: Browser) {
  const contexto = await browser.newContext({ baseURL: 'http://localhost:4200', locale: 'es-ES' });
  return contexto.newPage();
}

test('cierra la sesión de otro navegador desde «Sesiones»', async ({ page, browser }) => {
  const luis = cuenta('sesiones');
  const movil = await otroNavegador(browser);
  await conContrasena(movil, luis);
  await expect(movil).toHaveURL(/\/hogares/);

  await conContrasena(page, luis);
  await menu(page, 'Sesiones');
  await expect(page.getByRole('listitem')).toHaveCount(2);
  await page.getByRole('button', { name: 'Cerrar las demás sesiones' }).click();
  await expect(page.getByRole('listitem')).toHaveCount(1);

  await movil.reload(); // su refresh ya no renueva: a entrar otra vez
  await expect(movil).toHaveURL(/\/login/);
  await movil.context().close();
});
