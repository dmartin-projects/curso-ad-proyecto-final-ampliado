import { expect, test } from '@playwright/test';

import { entrar, estadisticasCaidas } from './ayuda';

test('la tarjeta del servicio de estadísticas', async ({ page }) => {
  await entrar(page);
  const tarjeta = page.locator('app-dias-semana');
  await tarjeta.scrollIntoViewIfNeeded();
  await expect(
    tarjeta.getByRole('img', { name: /Gasto medio por día de la semana/ }),
  ).toBeVisible();
  await expect(tarjeta).toContainText('servicio de estadísticas');
});

test('con el servicio de estadísticas caído, el resto del dashboard funciona', async ({ page }) => {
  await entrar(page, undefined, estadisticasCaidas);
  await expect(page.getByRole('region', { name: 'Resumen' })).toBeVisible(); // lo que viene de Django
  const tarjeta = page.locator('app-dias-semana');
  await tarjeta.scrollIntoViewIfNeeded();
  await expect(tarjeta.getByRole('status')).toContainText('no están disponibles');
  await expect(page.locator('mat-snack-bar-container')).toHaveCount(0); // ni un aviso de error global
});
