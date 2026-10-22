import { urlWebSocket } from './tiempo-real';

/** Módulo 86: el socket se abre donde diga el backend (la API), no donde esté la página (Vercel). */
describe('urlWebSocket', () => {
  const vercel = { protocol: 'https:', host: 'gastos.tudominio.com' };

  it('usa la URL pública que manda el backend en el ticket', () => {
    const url = urlWebSocket(
      { ticket: 'abc', caduca_en: 30, url: 'wss://api.gastos.tudominio.com/ws/notificaciones/' },
      vercel,
    );
    expect(url).toBe('wss://api.gastos.tudominio.com/ws/notificaciones/?ticket=abc');
  });

  it('sin URL en el ticket, el mismo host que la página (desarrollo y E2E)', () => {
    expect(urlWebSocket({ ticket: 'abc', caduca_en: 30, url: null }, vercel)).toBe(
      'wss://gastos.tudominio.com/ws/notificaciones/?ticket=abc',
    );
    expect(
      urlWebSocket(
        { ticket: 'abc', caduca_en: 30, url: null },
        { protocol: 'http:', host: 'localhost:4200' },
      ),
    ).toBe('ws://localhost:4200/ws/notificaciones/?ticket=abc');
  });

  it('el ticket va codificado en la query', () => {
    expect(urlWebSocket({ ticket: 'a+b/c=', caduca_en: 30, url: null }, vercel)).toContain(
      '?ticket=a%2Bb%2Fc%3D',
    );
  });
});
