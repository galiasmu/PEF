import concurrent.futures
import time
import random

def procesar_lote(lote, lote_id):
    """
    Procesa un lote de números calculando su suma.
    Simula un procesamiento que toma tiempo.
    """
    # Simular procesamiento que toma tiempo
    time.sleep(0.1)
    suma = sum(lote)
    return f"Lote {lote_id}: {lote} → Suma: {suma}"

def procesar_datos_paralelo(numeros, tamaño_lote=20, max_workers=4):
    """
    Procesa datos en lotes usando paralelismo con concurrent.futures.
    """
    # Dividir números en lotes
    lotes = []
    for i in range(0, len(numeros), tamaño_lote):
        lote = numeros[i:i + tamaño_lote]
        lotes.append((lote, len(lotes) + 1))
    
    print(f"Procesando {len(lotes)} lotes en paralelo con {max_workers} workers...")
    print("-" * 60)
    
    # Procesar lotes en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enviar todas las tareas
        futures = [executor.submit(procesar_lote, lote, lote_id) 
                  for lote, lote_id in lotes]
        
        # Recoger resultados conforme se completan
        for future in concurrent.futures.as_completed(futures):
            resultado = future.result()
            print(resultado)

# Crear lista de 100 números aleatorios
numeros = [random.randint(1, 100) for _ in range(100)]

# Procesar en lotes de 20 usando paralelismo
procesar_datos_paralelo(numeros, tamaño_lote=20, max_workers=4)