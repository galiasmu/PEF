def dividir_en_lotes_y_sumar(numeros, tamaño_lote=10):
    """
    Divide una lista de números en lotes y calcula la suma de cada lote.
    """
    lotes = []
    for i in range(0, len(numeros), tamaño_lote):
        lote = numeros[i:i + tamaño_lote]
        suma = sum(lote)
        lotes.append((lote, suma))
    
    return lotes

# Crear lista de números del 1 al 50
numeros = list(range(1, 51))

# Dividir en lotes de 10 y calcular sumas
lotes = dividir_en_lotes_y_sumar(numeros, 10)

# Imprimir resultados
for i, (lote, suma) in enumerate(lotes, 1):
    print(f"Lote {i}: {lote} → Suma: {suma}")