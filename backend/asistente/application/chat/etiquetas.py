# asistente/application/chat/etiquetas.py — lo que ve la persona mientras el agente trabaja (módulo 97)
#
# "Mirando el resumen del mes…" en vez de "resumen_mes {"mes": "2026-09"}". Un test comprueba que TODAS las tools del
# chat tienen la suya: una tool nueva sin etiqueta no pasa el CI.
ETIQUETAS = {
    "resumen_mes": "Mirando el resumen del mes",
    "gasto_por_categoria": "Sumando por categorías",
    "comparar_meses": "Comparando meses",
    "buscar_movimientos": "Buscando movimientos",
    "tendencia": "Mirando la evolución",
    "top_comercios": "Buscando dónde gastáis más",
    "estado_presupuestos": "Revisando los presupuestos",
    "prevision_fin_de_mes": "Calculando la previsión",
    "listar_categorias": "Mirando las categorías",
    "listar_cuentas": "Mirando las cuentas",
    "listar_miembros": "Mirando quién forma parte del hogar",
    "detalle_ticket": "Leyendo el ticket",
    "tipo_de_cambio": "Consultando el tipo de cambio del BCE",
    "comparar_con_ipc": "Consultando el IPC en Eurostat",
    "dias_festivos": "Consultando el calendario de festivos",
    "exportar": "Preparando el archivo",
    "grafico": "Preparando el gráfico",
    "proponer_movimiento": "Preparando el movimiento",
    "recordar": "Tomando nota",  # módulo 99
}
