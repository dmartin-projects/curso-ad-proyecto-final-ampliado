export const clavesAsistente = {
  conversaciones: (hogarId: number, carpeta: number | null) =>
    ['hogar', hogarId, 'asistente', 'conversaciones', carpeta ?? 'todas'] as const,
  carpetas: (hogarId: number) => ['hogar', hogarId, 'asistente', 'carpetas'] as const,
  todo: (hogarId: number) => ['hogar', hogarId, 'asistente'] as const,
};
