import elliptic_curve as ec
import random
from typing import Tuple



#Public parameter
curve = ec.P256
P = ec.P256.GPoint


def key(n:int) -> ec.Point:
    return ec.s_multiplication(curve, P, n)


def encryption(keyQ:ec.Point, msg:str) -> Tuple[list, list]:
    msg_points = ec.msg_to_points(curve,msg)
    
    shifts = []
    for point in msg_points:
        shifts.append(point.get_shift)
    
    k = random.randint(1, curve.p -1)
    c_1 = k * P
    
    encrypted = []
    for i in range(len(msg_points)):
        c_2 = msg_points[i] + (k * keyQ)
        encrypted.append((c_1,c_2))
        
    return encrypted, shifts 


def decryption(n:int, shifts:list, enc:list) -> str:
    
    decrypted = []
    for e in range(len(enc)):
        c_1, c_2 = enc[e]
        m = c_2 - (n * c_1)
        m = m.set_shift(shifts[e])

        decrypted.append(m)
          
    dec_str = ec.point_to_msg(decrypted)

    return dec_str




msg = "Ataturk came to prominence for his role in securing the Ottoman Turkish victory at the Battle of Gallipoli (1915) during World War I.[6] During this time, the Ottoman Empire perpetrated genocides against its Greek, Armenian and Assyrian subjects; while never involved, Ataturk's role in their aftermath was the subject of discussion. Following the defeat of the Ottoman Empire after World War I, he led the Turkish National Movement, which resisted mainland Turkey's partition among the victorious Allied powers."


keyQ = key(123)

enc, shifts = encryption(keyQ,msg)


print(f"\n\nENCRYPTED\n{enc}\nshifts: {shifts}")



dec = decryption(123,shifts,enc)
print(f"\n\nDECRYPTED\n{dec}")


if msg == dec:
    print("\n\nmessages match")
