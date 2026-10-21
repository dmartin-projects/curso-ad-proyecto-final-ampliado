/** Respuesta de GET /estadisticas/v1/hogares/{id}/dias-semana (el servicio de FastAPI, módulo 85). */
export interface DiasSemana {
  hogar_id: number;
  ultimo_evento: string | null;
  desde: string;
  hasta: string;
  dias: { dia: number; nombre: string; gasto_medio: string }[];
}
