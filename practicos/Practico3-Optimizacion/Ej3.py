# Funcion original

@profile
def procesar(lista):
    resultado = []
    for x in lista:
        if x % 2 == 0:
            resultado.append(x**2)
    return resultado

# las condicionales y el % haran mas lento el proceso, por lo tanto se presenta una nueva version optimizada con comprension y condicion

def procesar(lista):
    return [x*x for x in lista if x % 2 == 0]

 # Para ahorrar memoria si no se necesita la lista completa

def procesar_gen(lista):
    return (x * x for x in lista if (x & 1) == 0)
