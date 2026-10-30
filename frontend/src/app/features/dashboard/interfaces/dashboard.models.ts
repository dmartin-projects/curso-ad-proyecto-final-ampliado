import type { components } from '../../../core/api/esquema';
import { GraficoDeDatos } from '../../../shared/interfaces/grafico-de-datos';

/** Respuesta de GET /estadisticas/v1/hogares/{id}/dias-semana (el servicio de FastAPI, módulo 85). */
export interface DiasSemana {
  hogar_id: number;
  ultimo_evento: string | null;
  desde: string;
  hasta: string;
  dias: { dia: number; nombre: string; gasto_medio: string }[];
}

/** Un gráfico del chat fijado en el dashboard (módulo 97), con sus datos recalculados al pedirlo (o su error). */
export type GraficoFijado = Omit<components['schemas']['GraficoFijado'], 'grafico'> & {
  grafico: GraficoDeDatos | null;
};
