import cProfile

def suma_numeros_naturales(n):
    """
    Calcula la suma de los primeros n números naturales usando un bucle.
    """
    suma = 0
    for i in range(1, n + 1):
        suma += i
    return suma

def main():
    n = 1_000_000
    print(f"Calculando la suma de los primeros {n} números naturales...")
    
    # Ejecutar con cProfile
    cProfile.run('suma_numeros_naturales(1_000_000)', 'resultado_ej1.prof')
    
    # Mostrar resultado
    resultado = suma_numeros_naturales(n)
    print(f"Resultado: {resultado}")

if __name__ == "__main__":
    main()