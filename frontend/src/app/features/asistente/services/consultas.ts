export const clavesAsistente = {
  conversaciones: (hogarId: number, carpeta: number | null, q = '') =>
    ['hogar', hogarId, 'asistente', 'conversaciones', carpeta ?? 'todas', q] as const,
  carpetas: (hogarId: number) => ['hogar', hogarId, 'asistente', 'carpetas'] as const,
  recuerdos: (hogarId: number) => ['hogar', hogarId, 'asistente', 'recuerdos'] as const, // módulo 99
  cuota: (hogarId: number) => ['hogar', hogarId, 'asistente', 'cuota'] as const, // dentro de todo(): tras cada respuesta
  todo: (hogarId: number) => ['hogar', hogarId, 'asistente'] as const,
};
