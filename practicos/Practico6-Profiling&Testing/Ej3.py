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
def main():
    n = 10000  # Usamos un número más pequeño para que el profiling sea más claro
    print(f"Generando cuadrados de los primeros {n} números...")
    
    cuadrados = generar_cuadrados_lista(n)
    print(f"Se generaron {len(cuadrados)} cuadrados")
    print(f"Primeros 5 cuadrados: {cuadrados[:5]}")
    print(f"Últimos 5 cuadrados: {cuadrados[-5:]}")

if __name__ == "__main__":
    main()