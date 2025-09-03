def coin_change_combinations(total, coins, i=0, memo=None):
    if memo is None:
        memo = {}

    key = (i, total)
    if key in memo:
        return memo[key]

    # caso base: logramos formar el total
    if total == 0:
        return 1
    # caso base: sin monedas o total negativo
    if i >= len(coins) or total < 0:
        return 0

    # opción 1: usar la moneda coins[i]
    include = coin_change_combinations(total - coins[i], coins, i, memo)
    # opción 2: saltar a la siguiente moneda
    exclude = coin_change_combinations(total, coins, i + 1, memo)

    memo[key] = include + exclude
    return memo[key]


# Ejemplo de uso
coins = [1, 2, 5]
total = 5
print(coin_change_combinations(total, coins))  # 4

# Combinaciones:
# 5
# 2+2+1
# 2+1+1+1
# 1+1+1+1+1
