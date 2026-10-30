import type { components } from '../../../core/api/esquema';
import { GraficoDeDatos } from '../../../shared/interfaces/grafico-de-datos';

type S = components['schemas'];

export type Conversacion = S['Conversacion'];
export type ConversacionDetalle = S['ConversacionDetalle'];
export type Carpeta = S['Carpeta'];
export type Propuesta = S['Propuesta'];
export type Cuota = S['Cuota'];
export type Recuerdo = S['Recuerdo'];

/** Un gráfico del chat: los datos y QUÉ los produce (la especificación, para fijarlo en el dashboard). */
export interface GraficoDelChat extends GraficoDeDatos {
  fuente: string;
  argumentos: Record<string, unknown>;
}

export interface ArchivoDelChat {
  nombre: string;
  filas: number;
  url?: string; // firmada: caduca. Al abrir la conversación, la API da una nueva
}

/** Módulo 99: lo que la persona pidió recordar, en el momento en que el asistente lo guarda. */
export interface RecuerdoDelChat {
  id: number;
  texto: string;
}

/** Ejercicio 2 del 100: una sección de la ayuda que el asistente ha usado para contestar. */
export interface FuenteDeAyuda {
  fuente: string; // documento#sección
  titulo: string; // el del documento
}

/** Módulo 101: una consulta SQL del asistente y lo que devolvió («Ver los datos»). */
export interface ConsultaDelChat {
  sql: string;
  columnas: string[];
  filas: unknown[][];
  recortado: boolean;
}

export interface PropuestaDelChat {
  id: number;
  tipo: string;
  resumen: string;
  estado: 'pendiente' | 'confirmada' | 'descartada';
}

/** Lo que acompaña a una respuesta: lo que la interfaz pinta, no lo que lee el modelo. */
export interface DatosDelMensaje {
  graficos?: GraficoDelChat[];
  archivos?: ArchivoDelChat[];
  propuestas?: PropuestaDelChat[];
  recuerdos?: RecuerdoDelChat[];
  fuentes?: FuenteDeAyuda[];
  consultas?: ConsultaDelChat[];
  seguimiento?: string[];
}

export interface MensajeChat {
  id?: number;
  rol: 'usuario' | 'modelo';
  texto: string;
  datos: DatosDelMensaje;
  incompleto?: boolean;
  nombreAdjunto?: string;
}

/**
 * Los Server-Sent Events de POST …/preguntar/ (asistente/infrastructure/api/v1/views/preguntar_view.py). El nombre
 * del evento va en `evento` y no en `tipo`: los datos de un gráfico o de una propuesta ya traen su propio `tipo`.
 */
export type EventoChat =
  | { evento: 'inicio'; conversacion: number; pregunta: number }
  | { evento: 'tool'; nombre: string; texto: string }
  | { evento: 'texto'; delta: string }
  | ({ evento: 'grafico' } & GraficoDelChat)
  | ({ evento: 'archivo' } & ArchivoDelChat)
  | ({ evento: 'propuesta' } & PropuestaDelChat)
  | ({ evento: 'recuerdo' } & RecuerdoDelChat)
  | { evento: 'fuentes'; fuentes: FuenteDeAyuda[] }
  | ({ evento: 'datos' } & ConsultaDelChat)
  | { evento: 'titulo'; titulo: string }
  | ({ evento: 'fin'; mensaje: number; texto: string } & DatosDelMensaje)
  | { evento: 'error'; detalle: string };

/** Lo que la persona manda: el texto y, si quiere, una foto o un PDF. */
export interface Pregunta {
  texto: string;
  archivo?: File;
}
