import { expect, Page, test } from '@playwright/test';

import { DEMO, entrar, simularEstadisticas } from './ayuda';

/**
 * Módulo 91: entrar con Google y con Apple. Los dos son el proveedor OIDC falso (mock-oauth2-server, compose.yaml:
 * oidc): su pantalla de login acepta cualquier usuario (el `sub`) y los claims que se le escriban. Todo lo demás es de
 * verdad: la ida y la vuelta por Django (a través del proxy de ng serve, como en producción a través de Vercel), el
 * canje del code, la validación del ID token, la cookie del refresh y la SPA recuperando la sesión con ella.
 */
async function enElProveedor(page: Page, sub: string, claims: Record<string, unknown>) {
  await expect(page.getByText('Mock OAuth2 Server Sign-in')).toBeVisible();
  await page.locator('input[name=username]').fill(sub);
  await page.locator('textarea[name=claims]').fill(JSON.stringify(claims));
  await page.getByRole('button', { name: 'Sign-in' }).click();
}

async function conProveedor(
  page: Page,
  proveedor: 'Google' | 'Apple',
  sub: string,
  claims: object,
) {
  await simularEstadisticas(page);
  await page.goto('/login');
  await page.getByRole('link', { name: `Continuar con ${proveedor}` }).click();
  await enElProveedor(page, sub, claims);
}

test('una persona nueva entra con Google, se pone contraseña y quita Google', async ({ page }) => {
  await conProveedor(page, 'Google', 'google-nueva', {
    email: 'nueva@gmail.example',
    email_verified: true,
    given_name: 'Nueva',
  });
  await expect(page).toHaveURL(/\/hogares/); // dentro, sin contraseña: la cookie de refresh la ha puesto Django

  await page.getByRole('button', { name: 'Mi cuenta' }).click();
  await expect(page.getByText('nueva@gmail.example')).toBeVisible();
  await page.getByRole('menuitem', { name: 'Métodos de acceso' }).click();
  await expect(page.getByText('Tu cuenta no tiene contraseña: entras con Google.')).toBeVisible();
  const google = page.getByRole('listitem').filter({ hasText: 'nueva@gmail.example' });
  await expect(google.getByRole('button', { name: 'Desvincular' })).toBeDisabled(); // la única forma de entrar

  await page.getByLabel('Contraseña nueva').fill('una-clave-muy-larga-77');
  await page.getByRole('button', { name: 'Establecer contraseña' }).click();
  await expect(page.getByText('Tienes contraseña.')).toBeVisible();
  await google.getByRole('button', { name: 'Desvincular' }).click();
  await page.getByRole('alertdialog').getByRole('button', { name: 'Desvincular' }).click();
  await expect(page.getByText('nueva@gmail.example')).toHaveCount(0);
});

test('el email de una cuenta que ya existe no da acceso a ella; su dueño vincula Google desde dentro', async ({
  page,
}) => {
  // Alguien entra en "Google" con el email de demo: no entra en la cuenta de demo
  await conProveedor(page, 'Google', 'google-de-otro', { email: DEMO.email, email_verified: true });
  await expect(page).toHaveURL(/\/login\?error_social=cuenta_existente/);
  await expect(page.getByRole('alert')).toContainText(
    'Ya tienes una cuenta en Gastos con ese email',
  );

  // Demo entra con su contraseña y vincula SU Google (con otro email)
  await entrar(page);
  await page.goto('/acceso');
  await page
    .getByRole('listitem')
    .filter({ hasText: 'Google' })
    .getByRole('button', { name: 'Vincular' })
    .click();
  await enElProveedor(page, 'google-de-demo', {
    email: 'demo.personal@gmail.example',
    email_verified: true,
  });
  await expect(page).toHaveURL(/\/acceso$/);
  await expect(page.getByText('Cuenta de Google vinculada')).toBeVisible();
  await expect(page.getByText('demo.personal@gmail.example')).toBeVisible();

  // Desde ahora, "Continuar con Google" lleva a la cuenta de demo
  await page.getByRole('button', { name: 'Mi cuenta' }).click();
  await page.getByRole('menuitem', { name: 'Cerrar sesión' }).click();
  await conProveedor(page, 'Google', 'google-de-demo', { email: 'demo.personal@gmail.example' });
  await page.getByRole('button', { name: 'Mi cuenta' }).click();
  await expect(page.getByText(DEMO.email)).toBeVisible();
});

test('Apple vuelve con un POST (form_post) y la sesión se abre igual', async ({ page }) => {
  await conProveedor(page, 'Apple', 'apple-001234.abcd', {
    email: 'x7k2@privaterelay.appleid.com',
    email_verified: 'true', // Apple puede mandarlo como texto
  });
  await expect(page).toHaveURL(/\/hogares/);
  await page.getByRole('button', { name: 'Mi cuenta' }).click();
  await expect(page.getByText('x7k2@privaterelay.appleid.com')).toBeVisible();
});
