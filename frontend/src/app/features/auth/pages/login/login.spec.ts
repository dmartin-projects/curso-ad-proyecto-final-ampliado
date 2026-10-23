import { HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ProveedoresSociales } from '../../../../core/api/tipos';
import { Navegador } from '../../../../core/auth/social';
import { proveedoresDeTest } from '../../../../testing/proveedores';
import Login from './login';

/** Los enlaces a los proveedores (el login tiene otros: «Crear cuenta», «¿Has olvidado tu contraseña?»). */
const IDAS = 'a[href^="/api/v1/auth/social/"]';

const PROVEEDORES: ProveedoresSociales = {
  origen: 'https://gastos.example',
  proveedores: [
    { id: 'google', nombre: 'Google' },
    { id: 'apple', nombre: 'Apple' },
  ],
};

/** Módulo 91: los botones de Google, GitHub y Apple en el login, y lo que dice si la vuelta trae un error. */
describe('Login con proveedores', () => {
  let ctrl: HttpTestingController;

  function pintar(origen: string, entradas: Record<string, string> = {}) {
    TestBed.configureTestingModule({
      providers: [
        ...proveedoresDeTest(),
        { provide: Navegador, useValue: { origen: () => origen, ir: vi.fn() } },
      ],
    });
    ctrl = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(Login);
    for (const [nombre, valor] of Object.entries(entradas))
      fixture.componentRef.setInput(nombre, valor);
    ctrl.expectOne('/api/v1/auth/social/').flush(PROVEEDORES);
    fixture.detectChanges();
    return fixture.nativeElement as HTMLElement;
  }

  afterEach(() => ctrl.verify());

  it('enlaza con la ida de cada proveedor, llevando adónde volver', () => {
    const enlaces = [
      ...pintar('https://gastos.example', { volver: '/hogares/3' }).querySelectorAll(IDAS),
    ];
    expect(enlaces.map((a) => a.textContent?.trim())).toEqual([
      'Continuar con Google',
      'Continuar con Apple',
    ]);
    expect(enlaces[0].getAttribute('href')).toBe(
      '/api/v1/auth/social/google/entrar/?volver=%2Fhogares%2F3',
    );
  });

  it('en una preview de Vercel no los ofrece: su vuelta no está registrada', () => {
    const pagina = pintar('https://gastos-git-rama-equipo.vercel.app');
    expect(pagina.querySelectorAll(IDAS)).toHaveLength(0);
    expect(pagina.textContent).toContain(
      'El acceso con Google, Apple solo está disponible en https://gastos.example',
    );
  });

  it('explica por qué no ha entrado cuando vuelve con error_social', () => {
    const pagina = pintar('https://gastos.example', {
      error_social: 'cuenta_existente',
      proveedor: 'google',
    });
    expect(pagina.querySelector('[role=alert]')?.textContent).toContain(
      'Entra con tu contraseña y vincula Google desde «Métodos de acceso»',
    );
  });
});
