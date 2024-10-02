import elliptic_curve as ec
import hashlib

"""
    ECPRG takes an initial seed and a fixed generator point on an 
    elliptic curve to generate random elliptic curve points. 
    The x-coordinates of these points are concatenated and processed 
    (using modular arithmetic or hashing) to produce 
    secure and pseudo-random numbers
"""
def ec_pseudo_random(curve:ec.Curve, n:int) -> int:
    seed = curve.seed
    P = curve.GPoint

    points = []
    for i in range(n):
        Q = seed * P
        points.append(Q)
        seed += 1

    prand = ""
    for point in points:
        x = point.x
        prand += f"{str(x)}"

    prand_str = str(prand).encode('utf-8')
    hash_object = hashlib.md5(prand_str)
    hashed_prand = hash_object.hexdigest()
    prand = int(hashed_prand,16)

    return prand


#sample usage
print(ec_pseudo_random(ec.P256,10))
print(ec_pseudo_random(ec.P256,100))
