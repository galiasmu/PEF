from io import StringIO



def concatenar(lista):
    resultado = ""
    for palabra in lista:
        resultado += palabra
    return resultado


#Solucion mas simple
def concatenar(lista):
    return "".join(lista)

#Puede surgir problemas para grupos grandes de datos, por lo tanto tambien se puede hacer de la siguiente manera:


def concatenar(lista):
    buf = StringIO()
    for palabra in lista:
        buf.write(palabra)
    return buf.getvalue()
