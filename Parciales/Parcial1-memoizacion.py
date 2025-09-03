#!/usr/bin/env python3
"""
Asmuzi - Bossio
Comparación de performance de diferentes metodos para calcular números Fibonacci:
1. Recursivo (simple)
2. Memoizado (con cache)
3. Iterativo (bottom-up)
Incluye manejo de timeout para evitar ejecuciones excesivamente largas.
"""

import sys
import time
import threading
from typing import Dict, Optional, Tuple, Union


class TimeoutError(Exception):
    """Elevada cuando ocurre un timeout."""
    pass


class FibonacciCalculator:

    def __init__(self, recursion_limit: int = 10000):
        """Inicialización con límite de recurción personalizado."""
        sys.setrecursionlimit(recursion_limit)

    @staticmethod
    def recursive(n: int) -> int:
        """
        Calcula el número Fibonacci usando recursion simple.
        Complejidad de temporal: O(2^n) - Exponencial
        Complejidad espacial: O(n) - Debido a la pila de llamadas
        """
        if n <= 1:
            return n
        return FibonacciCalculator.recursive(n - 1) + FibonacciCalculator.recursive(n - 2)

    @staticmethod
    def memoized(n: int, memo: Optional[Dict[int, int]] = None) -> int:
        """
        Calcula el número Fibonacci usando memoización.
        Complejidad de temporal: O(n) - Lineal
        Complejidad espacial: O(n) - Para la tabla de memoización
        """
        if memo is None:
            memo = {}

        if n in memo:
            return memo[n]

        if n <= 1:
            return n

        memo[n] = FibonacciCalculator.memoized(n - 1, memo) + FibonacciCalculator.memoized(n - 2, memo)
        return memo[n]

    @staticmethod
    def iterative(n: int) -> int:
        """
        Calcula el número Fibonacci usando iteración.
        Complejidad de temporal: O(n) - Lineal
        Complejidad espacial: O(1) - Constante
        """
        if n <= 1:
            return n

        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


class PerformanceTimer:
    """Maneja el timing y la función de timeout para medir la performance."""

    @staticmethod
    def time_function(func, *args) -> Tuple[Union[int, None], float]:
        start_time = time.perf_counter()
        result = func(*args)
        end_time = time.perf_counter()
        return result, end_time - start_time

    @staticmethod
    def time_function_with_timeout(func, *args, timeout_seconds: float = 10) -> Tuple[Union[int, None], float, bool]:
        """
        Retorna:
            Tupla de (result, time_taken, timed_out)
        """
        result = [None]
        exception = [None]
        start_time = [None]
        end_time = [None]

        def target():
            try:
                start_time[0] = time.perf_counter()
                result[0] = func(*args)
                end_time[0] = time.perf_counter()
            except Exception as e:
                exception[0] = e
                end_time[0] = time.perf_counter()

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout_seconds)

        if thread.is_alive():
            # Thread is still running - timeout occurred
            return None, timeout_seconds, True

        if exception[0]:
            raise exception[0]

        return result[0], end_time[0] - start_time[0], False

    @staticmethod
    def format_time(seconds: float) -> str:
        """Formatea el tiempo en unidades más legibles."""
        if seconds >= 1:
            return f"{seconds:.6f} segundos"
        elif seconds >= 0.001:
            return f"{seconds * 1000:.3f} ms"
        elif seconds >= 0.000001:
            return f"{seconds * 1000000:.1f} μs"
        else:
            return f"{seconds * 1000000000:.1f} ns"


class FibonacciPerformanceComparison:
    """Ejecuta las pruebas."""

    def __init__(self, timeout_seconds: float = 10):
        self.calculator = FibonacciCalculator()
        self.timer = PerformanceTimer()
        self.timeout_seconds = timeout_seconds

    def _test_method(self, method_name: str, func, n: int, use_timeout: bool = False) -> None:
        """Testea un metodo Fibonacci e imprime los resultados."""
        try:
            if use_timeout:
                result, time_taken, timed_out = self.timer.time_function_with_timeout(
                    func, n, timeout_seconds=self.timeout_seconds
                )
                if timed_out:
                    print(f"  {method_name:<12}: TIMEOUT luego de {self.timeout_seconds} segundos - demasiado lento!")
                    return
            else:
                result, time_taken = self.timer.time_function(func, n)

            result_str = str(result)
            if len(result_str) > 50:
                result_str = result_str[:50] + "..."

            print(f"  {method_name:<12}: {result_str}")
            print(f"                (Tiempo: {self.timer.format_time(time_taken)})")

        except RecursionError:
            print(f"  {method_name:<12}: RecursionError - se alcanzo el limite de recursión")
        except KeyboardInterrupt:
            print(f"  {method_name:<12}: Interrumpido por el usuario")
            raise

    def run_comparison(self, test_numbers: list, use_timeout_for_recursive: bool = True) -> None:
        for n in test_numbers:
            print(f"\nCalculando F({n}):")

            # Test método recursivo (con timeout si es necesario)
            if n <= 50 or not use_timeout_for_recursive:
                self._test_method("Recursivo", self.calculator.recursive, n, use_timeout=use_timeout_for_recursive)
            else:
                print(f"  {'Recursivo':<12}: SKIPPED - demasiado lento para F({n})")

            # Test método memoizado
            self._test_method("Memoizado", self.calculator.memoized, n)

            # Test método iterativo
            self._test_method("Iterativo", self.calculator.iterative, n)

    def print_summary(self) -> None:
        """Imprime sumario de resultados."""
        print("\n" + "=" * 60)
        print("SUMARIO DE PERFORMANCE:")
        print("• Recursivo: O(2^n)  - Exponencial, se vuelve impráctico rápidamente")
        print("• Memoizado:  O(n)   - Lineal, usa memoria para cachear resultados")
        print("• Iterativo: O(n)    - Lineal, más eficiente en memoria")
        print(f"\nLimite de recurcion: {sys.getrecursionlimit():,}")
        print(f"\nNota de color: F(40) recursivamente hace ~1.6 billones de llamados a funcion")

def main():
    print("=== COMPARACION DE METODOS CON FIBONACCI ===\n")
    print("Recursivo, Memoizado e Iterativo\n")

    comparison = FibonacciPerformanceComparison(timeout_seconds=10)

    print("Pruebas con numeros pequeños:")
    small_tests = [5, 10, 15, 20, 25, 30]
    comparison.run_comparison(small_tests, use_timeout_for_recursive=True)

    print(f"\n{'=' * 60}")
    print("Pruebas con numeros medianos (el metodo recursivo se vuelve muy lento):")
    medium_tests = [32, 35, 38]
    comparison.run_comparison(medium_tests, use_timeout_for_recursive=True)

    print(f"\n{'=' * 60}")
    print("Pruebas con numeros grandes (solo metodo memoizado e iterativo):")
    large_tests = [100, 500, 1000]
    comparison.run_comparison(large_tests, use_timeout_for_recursive=True)

    print("Pruebas con numeros grandes secuenciales (solo metodo memoizado e iterativo):")
    print("- El objetivo es mostrar la mejora en performance del metodo memoizado en casos repetitivos -")
    repetitive_tests = [1000, 999, 998, 997, 996, 995]
    comparison.run_comparison(repetitive_tests, use_timeout_for_recursive=True)

    # Print final summary
    comparison.print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nComparacion interrumpida por el usuario.")
        sys.exit(1)