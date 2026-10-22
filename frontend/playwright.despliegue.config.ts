import { defineConfig, devices } from '@playwright/test';

/**
 * Prueba de humo contra un entorno YA desplegado (módulo 86, ejercicio 1): staging tras cada despliegue.
 *   HUMO_URL=https://staging.gastos.tudominio.com HUMO_EMAIL=… HUMO_PASSWORD=… \
 *   VERCEL_AUTOMATION_BYPASS_SECRET=… npx playwright test -c playwright.despliegue.config.ts
 * Sin servidores locales (no hay webServer): todo es el entorno de verdad, Vercel, Caddy y Django.
 */
export default defineConfig({
  testDir: 'e2e-despliegue',
  workers: 1,
  retries: 1, // la red de verdad puede fallar una vez; dos seguidas, no
  reporter: process.env['CI'] ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: {
    ...devices['Desktop Chrome'],
    baseURL: process.env['HUMO_URL'],
    locale: 'es-ES',
    trace: 'retain-on-failure',
    // Solo para ensayarlo en local (certificados propios y nombres .test); en el CI, vacíos
    ignoreHTTPSErrors: !!process.env['HUMO_LOCAL'],
    launchOptions: {
      ...(process.env['CHROMIUM_PATH'] ? { executablePath: process.env['CHROMIUM_PATH'] } : {}),
      args: process.env['HUMO_RESOLVER']
        ? [`--host-resolver-rules=${process.env['HUMO_RESOLVER']}`]
        : [],
    },
  },
});
