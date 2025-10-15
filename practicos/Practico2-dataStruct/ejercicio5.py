eventos = ["login", "click", "compra", "logout", "login", "click", "click"]
eventos_unicos_ordenados = []
vistos = set()

for evento in eventos:
    if evento not in vistos:
        eventos_unicos_ordenados.append(evento)
        vistos.add(evento)

print("Secuencia original:", eventos)
print("Secuencia sin duplicados y ordenada:", eventos_unicos_ordenados)



