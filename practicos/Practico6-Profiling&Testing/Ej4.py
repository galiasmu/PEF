from memory_profiler import profile

@profile
def generar_cuadrados_lista(n):
    """
    Genera una lista con los cuadrados de los primeros n números.
    """
    cuadrados = []
    for i in range(1, n + 1):
        cuadrados.append(i ** 2)
    return cuadrados

@profile
def generar_cuadrados_generador(n):
    """
    Genera un generador con los cuadrados de los primeros n números.
    """
    for i in range(1, n + 1):
        yield i ** 2

@profile
def main():
    n = 10000
    
    print("=== Método con lista ===")
    cuadrados_lista = generar_cuadrados_lista(n)
    print(f"Se generaron {len(cuadrados_lista)} cuadrados")
    
    print("\n=== Método con generador ===")
    cuadrados_gen = generar_cuadrados_generador(n)
    
    # Convertir generador a lista para comparar
    cuadrados_gen_lista = list(cuadrados_gen)
    print(f"Se generaron {len(cuadrados_gen_lista)} cuadrados")
    
    # Verificar que ambos métodos dan el mismo resultado
    print(f"¿Son iguales? {cuadrados_lista == cuadrados_gen_lista}")
    
    # Demostrar el uso del generador sin almacenar en memoria
    print("\n=== Usando generador sin almacenar en memoria ===")
    suma_cuadrados = 0
    for cuadrado in generar_cuadrados_generador(1000):
        suma_cuadrados += cuadrado
    print(f"Suma de los primeros 1000 cuadrados: {suma_cuadrados}")

if __name__ == "__main__":
    main()