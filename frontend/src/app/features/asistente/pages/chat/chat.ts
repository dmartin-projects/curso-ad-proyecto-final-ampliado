import {
  Component,
  computed,
  effect,
  ElementRef,
  inject,
  input,
  signal,
  untracked,
  viewChild,
} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { Router } from '@angular/router';
import { injectQuery, QueryClient } from '@tanstack/angular-query-experimental';
import { lastValueFrom } from 'rxjs';

import { HogarStore } from '../../../../core/hogar/hogar-store';
import { Avisos } from '../../../../core/http/avisos';
import { ErrorApi } from '../../../../core/http/errores';
import { Confirmaciones } from '../../../../shared/components/confirmar/confirmaciones';
import { MarkdownLigero } from '../../../../shared/pipes/markdown-ligero';
import { guardarArchivo } from '../../../../shared/utils/descargar';
import { CuotaDelAsistente } from '../../components/cuota/cuota';
import { Entrada } from '../../components/entrada/entrada';
import { GraficoDelChatCard } from '../../components/grafico-del-chat/grafico-del-chat';
import { ListaConversaciones } from '../../components/lista-conversaciones/lista-conversaciones';
import { Mensaje } from '../../components/mensaje/mensaje';
import { PropuestaCard } from '../../components/propuesta/propuesta';
import {
  Carpeta,
  Conversacion,
  GraficoDelChat,
  Pregunta,
  PropuestaDelChat,
} from '../../interfaces/asistente.models';
import { AsistenteApi } from '../../services/asistente-api';
import { ChatStore } from '../../services/chat-store';
import { clavesAsistente } from '../../services/consultas';

const SUGERENCIAS = [
  '¿Cuánto llevamos gastado este mes?',
  '¿En qué gastamos más que el mes pasado?',
  'Dibuja cómo han ido los gastos estos meses',
];

@Component({
  selector: 'app-chat',
  imports: [
    MatButtonModule,
    MatChipsModule,
    MatIconModule,
    MatProgressBarModule,
    MarkdownLigero,
    CuotaDelAsistente,
    Entrada,
    GraficoDelChatCard,
    ListaConversaciones,
    Mensaje,
    PropuestaCard,
  ],
  providers: [ChatStore],
  templateUrl: './chat.html',
})
export default class Chat {
  readonly conversacion = input<string>(); // ?conversacion=12
  protected readonly chat = inject(ChatStore);
  protected readonly hogar = inject(HogarStore);
  private readonly api = inject(AsistenteApi);
  private readonly avisos = inject(Avisos);
  private readonly confirmaciones = inject(Confirmaciones);
  private readonly queryClient = inject(QueryClient);
  private readonly router = inject(Router);
  protected readonly sugerencias = SUGERENCIAS;
  protected readonly hogarId = computed(() => this.hogar.activoId()!);
  protected readonly carpeta = signal<number | null>(null);
  protected readonly busqueda = signal('');
  protected readonly editando = signal(false);
  private readonly final = viewChild<ElementRef<HTMLElement>>('final');

  protected readonly conversaciones = injectQuery(() => ({
    queryKey: clavesAsistente.conversaciones(this.hogarId(), this.carpeta(), this.busqueda()),
    queryFn: () =>
      lastValueFrom(this.api.conversaciones(this.hogarId(), this.carpeta(), this.busqueda())),
  }));
  protected readonly cuota = injectQuery(() => ({
    queryKey: clavesAsistente.cuota(this.hogarId()),
    queryFn: () => lastValueFrom(this.api.cuota(this.hogarId())),
  }));
  protected readonly carpetas = injectQuery(() => ({
    queryKey: clavesAsistente.carpetas(this.hogarId()),
    queryFn: () => lastValueFrom(this.api.carpetas(this.hogarId())),
  }));

  constructor() {
    // La conversación de la URL. Si es la que ya está abierta (la que acaba de crear `enviar`), no se recarga:
    // la respuesta puede estar llegando
    effect(() => {
      const id = Number(this.conversacion()) || null;
      const hogarId = this.hogarId();
      untracked(() => {
        if (id === null) this.chat.vaciar(hogarId);
        else if (id !== this.chat.conversacionId()) void this.chat.abrir(hogarId, id);
      });
    });
    // Que se vea lo último que llega
    effect(() => {
      this.chat.mensajes();
      this.chat.borrador();
      this.final()?.nativeElement.scrollIntoView?.({ block: 'end' });
    });
  }

  protected async enviar(pregunta: Pregunta) {
    if (!this.chat.conversacionId()) {
      const id = await this.chat.nueva(this.hogarId());
      void this.router.navigate([], { queryParams: { conversacion: id } });
    }
    this.chat.preguntar(pregunta);
  }

  protected async nueva() {
    await this.router.navigate([], { queryParams: { conversacion: null } });
  }

  protected async resolver(propuesta: PropuestaDelChat, accion: 'confirmar' | 'descartar') {
    try {
      await this.chat.resolver(propuesta, accion);
      if (accion === 'confirmar') this.avisos.exito('Hecho: ya está apuntado.');
    } catch (e) {
      this.avisos.error(e instanceof ErrorApi ? e.titulo : 'No se ha podido.');
    }
  }

  protected async fijar(grafico: GraficoDelChat) {
    try {
      await this.chat.fijar(grafico);
      await this.queryClient.invalidateQueries({
        queryKey: ['hogar', this.hogarId(), 'graficos-fijados'],
      });
      this.avisos.exito('Fijado en el dashboard.');
    } catch (e) {
      if (e instanceof ErrorApi) this.avisos.error(e.titulo);
    }
  }

  protected async renombrar(titulo: string) {
    this.editando.set(false);
    if (titulo.trim() && titulo.trim() !== this.chat.titulo())
      await this.chat.renombrar(titulo.trim());
  }

  protected async crearCarpeta(nombre: string) {
    try {
      await lastValueFrom(this.api.crearCarpeta(this.hogarId(), nombre));
      await this.invalidar();
    } catch (e) {
      if (e instanceof ErrorApi) this.avisos.error(e.errores['nombre']?.[0] ?? e.titulo);
    }
  }

  protected async renombrarCarpeta({ carpeta, nombre }: { carpeta: Carpeta; nombre: string }) {
    try {
      await lastValueFrom(this.api.renombrarCarpeta(this.hogarId(), carpeta.id, nombre));
      await this.invalidar();
    } catch (e) {
      if (e instanceof ErrorApi) this.avisos.error(e.errores['nombre']?.[0] ?? e.titulo);
    }
  }

  protected async descargar(c: Conversacion) {
    guardarArchivo(await lastValueFrom(this.api.markdown(this.hogarId(), c.id)));
  }

  protected async borrarCarpeta(c: Carpeta) {
    const ok = await this.confirmaciones.preguntar(
      'Borrar la carpeta',
      `Las conversaciones de «${c.nombre}» no se borran: se quedan fuera de toda carpeta.`,
      'Borrar',
    );
    if (!ok) return;
    await lastValueFrom(this.api.borrarCarpeta(this.hogarId(), c.id));
    if (this.carpeta() === c.id) this.carpeta.set(null);
    await this.invalidar();
  }

  protected async mover({
    conversacion,
    carpeta,
  }: {
    conversacion: Conversacion;
    carpeta: number | null;
  }) {
    await lastValueFrom(this.api.modificar(this.hogarId(), conversacion.id, { carpeta }));
    await this.invalidar();
  }

  protected async borrar(c: Conversacion) {
    const ok = await this.confirmaciones.preguntar(
      'Borrar la conversación',
      `«${c.titulo || 'Conversación nueva'}» se borrará con todos sus mensajes.`,
      'Borrar',
    );
    if (!ok) return;
    await lastValueFrom(this.api.borrar(this.hogarId(), c.id));
    await this.invalidar();
    if (c.id === this.chat.conversacionId()) await this.nueva();
  }

  private invalidar() {
    return this.queryClient.invalidateQueries({ queryKey: clavesAsistente.todo(this.hogarId()) });
  }
}
