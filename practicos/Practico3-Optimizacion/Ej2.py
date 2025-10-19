import cProfile, pstats, io

def con_bucle(n):
    resultado = []
    for i in range(n):
        resultado.append(i*i)
    return resultado

def con_comprension(n):
    return [i*i for i in range(n)]

for fn in ("con_bucle(10**6)", "con_comprension(10**6)"):
    pr = cProfile.Profile()
    pr.enable()
    eval(fn, globals(), locals())
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
    ps.print_stats(10)
    print(f"\n=== {fn} ===")
    print(s.getvalue())

# Segun las pruebas realizadas, la version con comprension de listas es mas rapida que la version con bucle for tradicional.


