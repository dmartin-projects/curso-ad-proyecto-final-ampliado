import { HttpEventType } from '@angular/common/http';
import { HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { proveedoresDeTest } from '../../../testing/proveedores';
import { EventoChat } from '../interfaces/asistente.models';
import { AsistenteApi } from './asistente-api';

describe('AsistenteApi.preguntar (SSE con HttpClient, módulo 97)', () => {
  it('cada progreso de la descarga trae el texto recibido: salen los eventos nuevos', () => {
    TestBed.configureTestingModule({ providers: proveedoresDeTest() });
    const eventos: EventoChat[] = [];
    let terminado = false;
    TestBed.inject(AsistenteApi)
      .preguntar(3, 7, { texto: '¿Cuánto?' })
      .subscribe({ next: (e) => eventos.push(e), complete: () => (terminado = true) });

    const req = TestBed.inject(HttpTestingController).expectOne(
      '/api/v1/hogares/3/asistente/conversaciones/7/preguntar/',
    );
    expect(req.request.body).toEqual({ texto: '¿Cuánto?' });
    expect(req.request.reportProgress).toBe(true);
    const parte =
      'event: tool\ndata: {"nombre":"resumen_mes","texto":"Mirando"}\n\nevent: texto\ndata: {"delta":"Hola"}\n\n';
    req.event({ type: HttpEventType.DownloadProgress, loaded: parte.length, partialText: parte });
    expect(eventos.map((e) => e.evento)).toEqual(['tool', 'texto']);

    req.flush(parte + 'event: fin\ndata: {"mensaje":9,"texto":"Hola","seguimiento":[]}\n\n');
    expect(eventos.map((e) => e.evento)).toEqual(['tool', 'texto', 'fin']);
    expect(terminado).toBe(true);
  });

  it('con un adjunto, multipart', () => {
    TestBed.configureTestingModule({ providers: proveedoresDeTest() });
    const foto = new File(['jpg'], 'ticket.jpg', { type: 'image/jpeg' });
    TestBed.inject(AsistenteApi).preguntar(3, 7, { texto: 'mira', archivo: foto }).subscribe();
    const req = TestBed.inject(HttpTestingController).expectOne(() => true);
    const cuerpo = req.request.body as FormData;
    expect([cuerpo.get('texto'), (cuerpo.get('archivo') as File).name]).toEqual([
      'mira',
      'ticket.jpg',
    ]);
  });
});

describe('AsistenteApi, ejercicios del 97', () => {
  beforeEach(() => TestBed.configureTestingModule({ providers: proveedoresDeTest() }));

  it('busca con ?q= sin espacios, y sin q si no hay nada que buscar', () => {
    const api = TestBed.inject(AsistenteApi);
    const http = TestBed.inject(HttpTestingController);
    api.conversaciones(3, 5, '  cafe ').subscribe();
    api.conversaciones(3, null, '   ').subscribe();
    const [con, sin] = http.match((r) => r.url.endsWith('/conversaciones/'));
    expect([con.request.params.get('q'), con.request.params.get('carpeta')]).toEqual(['cafe', '5']);
    expect(sin.request.params.keys()).toEqual([]);
  });

  it('la conversación en Markdown, con el nombre que da el servidor', () => {
    const api = TestBed.inject(AsistenteApi);
    let nombre = '';
    api.markdown(3, 7).subscribe((a) => (nombre = a.nombre));
    TestBed.inject(HttpTestingController)
      .expectOne('/api/v1/hogares/3/asistente/conversaciones/7/markdown/')
      .flush(new Blob(['# Hola\n']), {
        headers: { 'Content-Disposition': 'attachment; filename="conversacion-7.md"' },
      });
    expect(nombre).toBe('conversacion-7.md');
  });

  it('renombrar una carpeta es un PATCH con el nombre', () => {
    TestBed.inject(AsistenteApi).renombrarCarpeta(3, 4, 'Lisboa').subscribe();
    const req = TestBed.inject(HttpTestingController).expectOne(
      '/api/v1/hogares/3/asistente/carpetas/4/',
    );
    expect([req.request.method, req.request.body]).toEqual(['PATCH', { nombre: 'Lisboa' }]);
  });
});
