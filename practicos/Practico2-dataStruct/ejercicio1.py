import time

# Crea una lista grande y un conjunto para comparar
numeros_lista = list(range(1000000))
numeros_conjunto = set(numeros_lista)
numero_a_buscar = 999999

# Búsqueda en la lista (ineficiente)
inicio = time.time()
resultado_lista = numero_a_buscar in numeros_lista
fin = time.time()
print(f"Tiempo de búsqueda en lista: {fin - inicio:.6f} segundos")

# Búsqueda en el conjunto (eficiente)
inicio = time.time()
resultado_conjunto = numero_a_buscar in numeros_conjunto
fin = time.time()
print(f"Tiempo de búsqueda en conjunto: {fin - inicio:.6f} segundos")

