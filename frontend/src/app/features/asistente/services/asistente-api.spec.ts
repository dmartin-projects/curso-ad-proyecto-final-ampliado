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
