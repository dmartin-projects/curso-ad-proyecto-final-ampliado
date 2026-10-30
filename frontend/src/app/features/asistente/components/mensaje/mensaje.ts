import { Component, input, output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';

import { MarkdownLigero } from '../../../../shared/pipes/markdown-ligero';
import { GraficoDelChat, MensajeChat, PropuestaDelChat } from '../../interfaces/asistente.models';
import { GraficoDelChatCard } from '../grafico-del-chat/grafico-del-chat';
import { PropuestaCard } from '../propuesta/propuesta';

/** Un mensaje del chat: el texto (Markdown ligero, escapado) y lo que lo acompaña. */
@Component({
  selector: 'app-mensaje',
  imports: [
    MatButtonModule,
    MatChipsModule,
    MatIconModule,
    MarkdownLigero,
    GraficoDelChatCard,
    PropuestaCard,
  ],
  templateUrl: './mensaje.html',
  host: { class: 'block' },
})
export class Mensaje {
  readonly mensaje = input.required<MensajeChat>();
  readonly ultimo = input(false); // las preguntas de seguimiento, solo en la última respuesta
  readonly ocupado = input(false);
  readonly puedeFijar = input(true);
  readonly confirmar = output<PropuestaDelChat>();
  readonly descartar = output<PropuestaDelChat>();
  readonly fijar = output<GraficoDelChat>();
  readonly seguir = output<string>();

  /** «tickets#Subir un ticket» → «Subir un ticket» (ejercicio 2 del 100). */
  protected seccion(fuente: string): string {
    return fuente.split('#')[1] ?? fuente;
  }
}
