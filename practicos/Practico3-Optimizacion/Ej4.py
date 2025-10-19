from array import array

#Codigo original
from memory_profiler import profile

@profile
def crear_listas():
    a = [i for i in range(10**6)]
    b = [i*2 for i in range(10**6)]
    return a, b

#Podemos optimizarlo removiendo el bucle for
@profile
def crear_iterables():
    a = range(10**6)                 # objeto “ligero”
    b = (i*2 for i in range(10**6))  # generador
    return a, b


# Optimizacion 2 para ahorrar memoria:
@profile
def crear_arrays():
    n = 10**6
    a = array('I', range(n))
    b = array('I', (i*2 for i in range(n)))
    return a, b
