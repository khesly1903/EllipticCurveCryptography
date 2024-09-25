import elliptic_curve as ec
import random
from typing import Tuple


class ElGamal:
    def __init__(self, curve):
        self.curve = curve
        self.P = curve.GPoint

    def key(self, n: int) -> ec.Point:
        return ec.s_multiplication(self.curve, self.P, n)

    def encryption(self, keyQ: ec.Point, msg: str) -> Tuple[list, list]:
        msg_points = ec.msg_to_points(self.curve, msg)
        
        shifts = []
        for point in msg_points:
            shifts.append(point.get_shift)
        
        k = random.randint(1, self.curve.p - 1)
        c_1 = k * self.P
        
        encrypted = []
        for i in range(len(msg_points)):
            c_2 = msg_points[i] + (k * keyQ)
            encrypted.append((c_1, c_2))  
            
        return shifts, encrypted 

    def decryption(self, n: int, shifts: list, enc: list) -> str:
        decrypted = []
        for e in range(len(enc)):
            c_1, c_2 = enc[e]
            m = c_2 - (n * c_1)
            m = m.set_shift(shifts[e])
            decrypted.append(m)
        
        return ec.point_to_msg(decrypted)



