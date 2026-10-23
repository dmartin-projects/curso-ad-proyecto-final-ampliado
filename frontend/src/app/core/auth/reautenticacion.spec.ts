import { HttpClient } from '@angular/common/http';
import { HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { proveedoresDeTest } from '../../testing/proveedores';
import { ErrorApi } from '../http/errores';
import { AuthStore } from './auth-store';
import { Reautenticacion } from './reautenticacion';

/** El reto del RFC 9470 tal cual lo manda Django (módulo 92). */
const STEP_UP = {
  status: 401,
  statusText: 'Unauthorized',
  headers: {
    'WWW-Authenticate':
      'Bearer realm="api", error="insufficient_user_authentication", max_age="300"',
  },
};

/** Módulo 92: el step-up. Confirmar y repetir la petición; nunca confundirlo con un access caducado. */
describe('reautenticacionInterceptor', () => {
  let http: HttpClient;
  let ctrl: HttpTestingController;
  let confirmar: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    confirmar = vi.fn();
    TestBed.configureTestingModule({
      providers: [...proveedoresDeTest(), { provide: Reautenticacion, useValue: { confirmar } }],
    });
    http = TestBed.inject(HttpClient);
    ctrl = TestBed.inject(HttpTestingController);
    TestBed.inject(AuthStore).login('a@b.c', 'x').subscribe();
    ctrl.expectOne('/api/v1/auth/login/').flush({ access: 'token' });
    ctrl.expectOne('/api/v1/auth/me/').flush({ id: 1, email: 'a@b.c', es_personal: false });
  });

  afterEach(() => ctrl.verify());

  const vuelta = () => new Promise((r) => setTimeout(r));

  it('pide confirmar y repite la misma petición, con el mismo token', async () => {
    confirmar.mockResolvedValue(true);
    let respuesta: unknown;
    http.post('/api/v1/auth/seguridad/totp/', null).subscribe((r) => (respuesta = r));
    ctrl
      .expectOne('/api/v1/auth/seguridad/totp/')
      .flush({ type: 'reautenticacion_requerida' }, STEP_UP);
    await vuelta();
    expect(confirmar).toHaveBeenCalledOnce();
    const repetida = ctrl.expectOne('/api/v1/auth/seguridad/totp/');
    expect(repetida.request.headers.get('Authorization')).toBe('Bearer token'); // la sesión, ya "reciente"
    repetida.flush({ secreto: 'ABC' });
    expect(respuesta).toEqual({ secreto: 'ABC' });
  });

  it('si no confirma, el 401 llega a quien llamó y NO se intenta un refresh', async () => {
    confirmar.mockResolvedValue(false);
    let error: unknown;
    http.delete('/api/v1/hogares/3/').subscribe({ error: (e) => (error = e) });
    ctrl
      .expectOne('/api/v1/hogares/3/')
      .flush({ type: 'reautenticacion_requerida', title: 'Confirma' }, STEP_UP);
    await vuelta();
    ctrl.expectNone('/api/v1/auth/refresh/'); // no es un access caducado
    expect(error).toBeInstanceOf(ErrorApi);
    expect((error as ErrorApi).tipo).toBe('reautenticacion_requerida');
  });

  it('un 401 normal sigue siendo un access caducado: refresh, no confirmar', () => {
    http.get('/api/v1/a/').subscribe();
    ctrl.expectOne('/api/v1/a/').flush({}, { status: 401, statusText: 'Unauthorized' });
    ctrl.expectOne('/api/v1/auth/refresh/').flush({ access: 'nuevo' });
    ctrl.expectOne('/api/v1/a/').flush({});
    expect(confirmar).not.toHaveBeenCalled();
  });
});
