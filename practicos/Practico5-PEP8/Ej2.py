"""Módulo con función de suma siguiendo PEP 8."""


def suma(a, b):
    """
    Suma dos números.

    Args:
        a (int/float): Primer número.
        b (int/float): Segundo número.

    Returns:
        int/float: Suma de a y b.
    """
    return a + b


if __name__ == "__main__":
    resultado = suma(3, 4)
    print(resultado)
