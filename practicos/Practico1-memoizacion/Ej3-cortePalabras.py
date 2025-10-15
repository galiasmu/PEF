def word_break(s, word_dict, memo=None):
    if memo is None:
        memo = {}
    if s in memo:
        return memo[s]

    # caso base: string vacio se puede formar
    if not s:
        return True

    for word in word_dict:
        if s.startswith(word):  # si el prefijo coincide
            if word_break(s[len(word):], word_dict, memo):
                memo[s] = True
                return True

    memo[s] = False
    return False


s = "applepenapple"
word_dict = ["apple", "pen"]
print(word_break(s, word_dict))  # True (porque "apple pen apple")

s2 = "catsandog"
word_dict2 = ["cats", "dog", "sand", "and", "cat"]
print(word_break(s2, word_dict2))  # False
