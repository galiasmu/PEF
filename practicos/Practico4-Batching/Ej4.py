def enviar_mensajes_por_lotes(mensajes, tamaño_lote=5):
    """
    Envía mensajes en lotes y marca cada lote como enviado.
    """
    lote_numero = 1
    
    for i in range(0, len(mensajes), tamaño_lote):
        lote = mensajes[i:i + tamaño_lote]
        print(f"Enviando lote {lote_numero}: {lote}")
        print(f"✅ Lote {lote_numero} enviado exitosamente")
        print("-" * 40)
        lote_numero += 1

# Crear cola de 27 mensajes
mensajes = [f"msg_{i}" for i in range(1, 28)]

# Enviar mensajes en lotes de 5
enviar_mensajes_por_lotes(mensajes, 5)