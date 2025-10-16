def simular_insercion_bd(registros, tamaño_lote=200):
    """
    Simula la inserción de registros en una base de datos en lotes.
    """
    total_registros = len(registros)
    lote_numero = 1
    
    for i in range(0, total_registros, tamaño_lote):
        lote = registros[i:i + tamaño_lote]
        print(f"Insertando lote {lote_numero}: {len(lote)} registros")
        print(f"  Registros: {lote[:5]}{'...' if len(lote) > 5 else ''}")
        print(f"  ✅ Lote {lote_numero} insertado exitosamente")
        print("-" * 50)
        lote_numero += 1

# Crear 1000 registros de ejemplo
registros = [f"registro_{i:04d}" for i in range(1, 1001)]

# Simular inserción en lotes de 200
simular_insercion_bd(registros, 200)