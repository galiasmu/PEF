import time


def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a+b
    return a

inicio = time.time()
print(fibonacci(10**6))
print("Tiempo:", time.time() - inicio)



def fib_fast_doubling(n):
    if n == 0:
        return (0, 1)
    a, b = fib_fast_doubling(n >> 1)
    c = a * ((b << 1) - a)
    d = a*a + b*b
    return (d, c + d) if (n & 1) else (c, d)

inicio = time.time()
print("Dígitos:", len(str(fib_fast_doubling(10**6)[0])))
print("Tiempo:", time.time() - inicio)
