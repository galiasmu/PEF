def suma(int n):
    cdef long long total = 0
    cdef int i
    for i in range(n):
        total += i
    return total
