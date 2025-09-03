from functools import lru_cache
from time import perf_counter


def caminos_recursivo(m: int, n: int) -> int:
    """Versión recursiva pura (sin memo). Complejidad exponencial."""
    if m <= 0 or n <= 0:
        return 0

    def f(i: int, j: int) -> int:
        if i == 0 or j == 0:
            return 1
        return f(i-1, j) + f(i, j-1)

    return f(m-1, n-1)


def caminos_memo(m: int, n: int) -> int:
    """Versión recursiva con memoización. Complejidad O(m·n)."""
    if m <= 0 or n <= 0:
        return 0

    @lru_cache(maxsize=None)
    def f(i: int, j: int) -> int:
        if i == 0 or j == 0:
            return 1
        return f(i-1, j) + f(i, j-1)

    return f(m-1, n-1)
#Hasta aca solucion, lo siguiente son calculos para comprobar tiempo

# -----------------------
# 2) Medición de tiempos
# -----------------------
def time_call(fn, *args, repeats: int = 3):
    """
    Corre la función 'repeats' veces y devuelve (resultado, mejor_tiempo_en_segundos).
    Usamos el mejor tiempo para reducir ruido.
    """
    result = None
    best = float("inf")
    for _ in range(repeats):
        t0 = perf_counter()
        result = fn(*args)
        dt = perf_counter() - t0
        if dt < best:
            best = dt
    return result, best


def comparar(m: int, n: int, repeats: int = 3):
    """
    Compara recursivo vs memo en (m, n), valida que ambos den el mismo resultado
    y muestra tiempos.
    """
    print(f"Comparando para m={m}, n={n} (repeats={repeats})")

    # Memo
    res_memo, t_memo = time_call(caminos_memo, m, n, repeats=repeats)

    # Recursivo puro (¡ojo con tamaños grandes!)
    res_rec, t_rec = time_call(caminos_recursivo, m, n, repeats=repeats)

    assert res_memo == res_rec, f"Resultados diferentes: memo={res_memo}, rec={res_rec}"

    print(f"Resultado: {res_memo}")
    print(f"Memoización: {t_memo:.6f} s")
    print(f"Recursivo puro: {t_rec:.6f} s")
    speedup = (t_rec / t_memo) if t_memo > 0 else float('inf')
    print(f"Speedup (rec / memo): ×{speedup:.1f}")


# -----------------------
# 3) Ejemplos de uso
# -----------------------
if __name__ == "__main__":
    # Elegí tamaños prudentes para el recursivo puro (crece MUY rápido).
    comparar(8, 8)     # razonable para recursivo puro
    # comparar(10, 10) # puede tardar bastante sin memo; activalo si querés probar
    # comparar(12, 12) # probablemente muy lento en recursivo puro
