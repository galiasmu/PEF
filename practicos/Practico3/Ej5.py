def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a+b
    return a

import time
inicio = time.time()
print(fibonacci(10**6))
print("Tiempo:", time.time() - inicio)