import cProfile

def suma_numeros_naturales_lenta(n):
    """
    Calcula la suma de los primeros n números naturales usando un bucle.
    """
    suma = 0
    for i in range(1, n + 1):
        suma += i
    return suma

def suma_numeros_naturales_optimizada(n):
    """
    Calcula la suma de los primeros n números naturales usando la fórmula matemática.
    suma(n) = (n*(n+1))/2
    """
    return (n * (n + 1)) // 2

def main():
    n = 1_000_000
    print(f"Comparando métodos para calcular la suma de los primeros {n} números naturales...")
    
    # Profiling del método lento
    print("\n=== Profiling del método con bucle ===")
    cProfile.run('suma_numeros_naturales_lenta(1_000_000)', 'resultado_lento.prof')
    
    # Profiling del método optimizado
    print("\n=== Profiling del método optimizado ===")
    cProfile.run('suma_numeros_naturales_optimizada(1_000_000)', 'resultado_optimizado.prof')
    
    # Verificar que ambos métodos dan el mismo resultado
    resultado_lento = suma_numeros_naturales_lenta(n)
    resultado_optimizado = suma_numeros_naturales_optimizada(n)
    
    print(f"\nResultado método lento: {resultado_lento}")
    print(f"Resultado método optimizado: {resultado_optimizado}")
    print(f"¿Son iguales? {resultado_lento == resultado_optimizado}")

if __name__ == "__main__":
    main()