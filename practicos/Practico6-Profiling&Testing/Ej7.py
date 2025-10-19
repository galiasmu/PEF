import doctest

def es_primo(n):
    """
    Determina si un número n es primo.
    
    Args:
        n (int): Número a verificar
        
    Returns:
        bool: True si n es primo, False en caso contrario
        
    Examples:
        >>> es_primo(2)
        True
        >>> es_primo(3)
        True
        >>> es_primo(4)
        False
        >>> es_primo(5)
        True
        >>> es_primo(6)
        False
        >>> es_primo(7)
        True
        >>> es_primo(8)
        False
        >>> es_primo(9)
        False
        >>> es_primo(10)
        False
        >>> es_primo(11)
        True
        >>> es_primo(1)
        False
        >>> es_primo(0)
        False
        >>> es_primo(-1)
        False
        >>> es_primo(97)
        True
        >>> es_primo(100)
        False
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Verificar divisores impares hasta la raíz cuadrada de n
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def main():
    # Ejecutar doctest
    doctest.testmod(verbose=True)

if __name__ == "__main__":
    main()