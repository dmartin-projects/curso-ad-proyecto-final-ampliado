import { expect, Page, test } from '@playwright/test';

import { entrar, vigilarConsola } from './ayuda';

/**
 * Módulo 97: el chat con el backend de verdad. El LLM es una vista del propio backend de E2E (config/urls_e2e.py:
 * llm_falso) que contesta como Chat Completions, también en streaming: aquí se prueba la aplicación, no el modelo.
 */
async function preguntar(page: Page, texto: string) {
  await page.getByRole('textbox', { name: 'Pregunta' }).fill(texto);
  await page.getByRole('button', { name: 'Enviar' }).click();
}

async function abrirAsistente(page: Page) {
  await entrar(page);
  await page.getByRole('link', { name: 'Asistente' }).click();
  await expect(page.getByRole('heading', { name: 'Asistente' })).toBeVisible();
}

test('una conversación: la respuesta llega, se titula sola y se sigue con una sugerencia', async ({
  page,
}) => {
  const sinErrores = vigilarConsola(page);
  await abrirAsistente(page);
  await preguntar(page, '¿Cuánto llevamos gastado este mes?');

  const respuestas = page.getByRole('article', { name: 'Respuesta del asistente' });
  await expect(respuestas.first()).toContainText(/gastasteis [\d.,]+ €/);
  await expect(page.getByRole('heading', { name: 'Gastos del mes' })).toBeVisible(); // el título, del modelo pequeño
  await expect(page).toHaveURL(/\/asistente\?conversacion=\d+$/);
  await expect(page.getByRole('navigation', { name: 'Conversaciones' })).toContainText(
    'Gastos del mes',
  );

  await page
    .getByRole('option', { name: '¿Y en agosto?' })
    .or(page.getByText('¿Y en agosto?'))
    .first()
    .click();
  await expect(respuestas.nth(1)).toContainText('En 2026-08 gastasteis');

  await page.reload(); // todo guardado: las dos preguntas y las dos respuestas
  await expect(respuestas).toHaveCount(2);
  sinErrores();
});

test('un gráfico del chat, fijado en el dashboard y quitado', async ({ page }) => {
  await abrirAsistente(page);
  await preguntar(page, 'Dibuja cómo van los gastos');
  const grafico = page.getByRole('figure').filter({ hasText: 'Gastos de los últimos meses' });
  await expect(grafico.locator('canvas')).toBeVisible();
  await grafico.getByRole('button', { name: 'Fijar en el dashboard' }).click();
  await expect(page.getByText('Fijado en el dashboard.')).toBeVisible();

  await page.getByRole('link', { name: 'Resumen' }).click();
  const fijados = page.getByRole('region', { name: 'Gráficos fijados desde el asistente' });
  await expect(fijados).toContainText('Gastos de los últimos meses');
  await expect(fijados.locator('canvas')).toBeVisible();
  await fijados.getByRole('button', { name: 'Quitar del dashboard' }).click();
  await expect(fijados).toBeHidden();
});

test('apuntar un gasto: nada cambia hasta que la persona confirma', async ({ page }) => {
  await abrirAsistente(page);
  await preguntar(page, 'Apunta 3,50 € de churros');
  const propuesta = page.getByRole('group', { name: 'Propuesta del asistente' });
  await expect(propuesta).toContainText('Gasto de 3,50 €: «Churros»');
  await propuesta.getByRole('button', { name: 'Confirmar' }).click();
  await expect(propuesta).toContainText('Confirmada');

  await page.getByRole('link', { name: 'Movimientos' }).click();
  await page.getByRole('searchbox', { name: 'Buscar' }).fill('Churros');
  await expect(page.locator('[data-fila]', { hasText: 'Churros' })).toContainText('-3,50 €');
});

test('detener una respuesta a medias', async ({ page }) => {
  await abrirAsistente(page);
  await preguntar(page, 'Una respuesta lenta, por favor');
  await expect(page.getByText('Esta respuesta llega')).toBeVisible(); // ya está llegando
  await page.getByRole('button', { name: 'Detener' }).click();
  await expect(page.getByText('Sin respuesta: no se completó.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Enviar' })).toBeVisible();
  // Y el servidor se ha enterado: ha dejado de pedir texto al modelo y ha marcado la pregunta como incompleta
  await expect(async () => {
    await page.reload();
    await expect(page.getByText('Sin respuesta: no se completó.')).toBeVisible({ timeout: 5000 });
  }).toPass({ timeout: 20_000 }); // cada recarga arranca la app entera: unos segundos con `ng serve`
});

test('ejercicios del 97: buscar, renombrar una carpeta y descargar en Markdown', async ({
  page,
}) => {
  await abrirAsistente(page);
  await preguntar(page, '¿Cuánto llevamos gastado este mes?');
  await expect(page.getByRole('heading', { name: 'Gastos del mes' })).toBeVisible();
  const lista = page.getByRole('navigation', { name: 'Conversaciones' });

  await lista.getByRole('searchbox', { name: 'Buscar' }).fill('GASTADO');
  await expect(lista.getByRole('link', { name: /Gastos del mes/ }).first()).toBeVisible();
  await lista.getByRole('searchbox', { name: 'Buscar' }).fill('zzz-nada');
  await expect(lista).toContainText('Ninguna conversación lo menciona.');
  await lista.getByRole('searchbox', { name: 'Buscar' }).fill('');

  const nombre = `Viaje ${Date.now()}`;
  await lista.getByRole('textbox', { name: 'Nueva carpeta' }).fill(nombre);
  await lista.getByRole('button', { name: 'Crear la carpeta' }).click();
  await lista.getByRole('option', { name: new RegExp(nombre) }).click();
  await lista.getByRole('button', { name: `Renombrar «${nombre}»` }).click();
  await lista.getByRole('textbox').last().fill(`${nombre} a Lisboa`);
  await lista.getByRole('button', { name: 'Guardar el nombre' }).click();
  await expect(lista.getByRole('option', { name: new RegExp(`${nombre} a Lisboa`) })).toBeVisible();
  await lista.getByRole('option', { name: new RegExp(`${nombre} a Lisboa`) }).click(); // fuera el filtro

  await lista.getByRole('button', { name: 'Opciones de Gastos del mes' }).first().click();
  const descarga = page.waitForEvent('download');
  await page.getByRole('menuitem', { name: 'Descargar en Markdown' }).click();
  expect((await descarga).suggestedFilename()).toMatch(/^conversacion-\d+\.md$/);
});

test('sin cuota: el aviso, y la pregunta no sale (un 429 antes del stream)', async ({
  page,
  request,
}) => {
  await abrirAsistente(page);
  await request.post('http://localhost:8000/e2e/asistente/cuota');
  try {
    await page.reload();
    await expect(
      page.getByRole('status').filter({ hasText: 'límite de preguntas de hoy' }),
    ).toBeVisible();
    await preguntar(page, '¿Cuánto llevamos gastado este mes?');
    await expect(page.getByRole('alert')).toContainText(
      'Has llegado al límite de preguntas de hoy. Mañana vuelves a tenerlo.',
    );
  } finally {
    await request.delete('http://localhost:8000/e2e/asistente/cuota');
  }
});

test('la memoria: «recuerda que…», se ve en la lista y se olvida', async ({ page }) => {
  await abrirAsistente(page);
  await preguntar(page, 'Recuerda que la cuenta común es la de ING');
  await expect(page.getByRole('note')).toContainText(
    'Lo recordaré: «La cuenta común es la de ING.»',
  );

  await page.getByText('Lo que recuerda el asistente (1)').click();
  const lista = page.getByRole('list', { name: 'Recuerdos' });
  await expect(lista).toContainText('La cuenta común es la de ING.');
  await lista.getByRole('button', { name: 'Olvidar «La cuenta común es la de ING.»' }).click();
  await expect(page.getByText('Lo que recuerda el asistente (0)')).toBeVisible();
});
