
# https://github.com/darkwallet/python-obelisk/blob/5812ccfd78a66963f7238d9835607908a8c8f392/obelisk/numbertheory.py
     
def inv(a,q):
    if a == q:
        raise ValueError("not invertible")
    elif a > q:
        a %= q
        return pow(a,-1,q)
    elif a < q:
        return pow(a,-1,q)

    

def modsqrt(a, p):

    if legendre_symbol(a, p) != 1:
        return 0
    elif a == 0:
        return 0
    elif p == 2:
        return p
    elif p % 4 == 3:
        return pow(a, (p + 1) // 4, p)


    s = p - 1
    e = 0
    while s % 2 == 0:

        s //= 2
        e += 1


    n = 2
    while legendre_symbol(n, p) != -1:
        n += 1


    x = pow(a, (s + 1) // 2, p)
    b = pow(a, s, p)
    g = pow(n, s, p)
    r = e

    while True:
        t = b
        m = 0
        for m in range(r):
            if t == 1:
                break
            t = pow(t, 2, p)

        if m == 0:
            return x

        gs = pow(g, 2 ** (r - m - 1), p)
        g = (gs * gs) % p
        x = (x * gs) % p
        b = (b * g) % p
        r = m


def legendre_symbol(a, p):

    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls
def binary(k):
    binary = bin(k).replace("0b","") 
    binary_arr = []
    for bit in binary:
        bit = int(bit) 
        binary_arr.append(bit)

    return binary_arr
