import numpy as np
import ecc_math


bit_num = 32


class Curve:
    def __init__(self, a: int, b: int, p: int, Gx: int, Gy: int):
        self.a = a
        self.b = b
        self.p = p
        self.Gx = Gx
        self.Gy = Gy

        # Non-singularity test
        if (4 * pow(self.a, 3) + 27 * pow(self.b, 2)) % self.p == 0:
            raise ValueError("Curve is singular")

    @property
    def GPoint(self) -> "Point":
        return Point(self, self.Gx, self.Gy) 


class Point(Curve):
    def __init__(self, curve: Curve, x: int, y: int, shift:int = 0):
        self.curve = curve
        self._x = x  
        self._y = y  
        self.shift = shift
        
        # Check if the point is on the curve (or it is point at infinity)
        if (x == np.inf and y == np.inf) or pow(y, 2, curve.p) == (pow(x, 3, curve.p) + curve.a * x + curve.b) % curve.p:
            pass
        else:
            raise ValueError("Point is not on curve")

    @property
    def x(self) -> int:
        return self._x  

    @property
    def y(self) -> int:
        return self._y  
    
    @property
    def unshift(self) -> int:
        return self.x - self.shift 
    
    @property
    def get_shift(self) -> int:
        return self.shift
    
    def set_shift(self, shift: int) -> "Point":
        self.shift = shift
        return self
        
    

    def get_msg(self, shift: int) -> int:
        return self.x - shift
        

    def compute_y(self, x:int) -> int:
        right = (x * x * x + self.a * x + self.b) % self.p
        y = ecc_math.modsqrt(right, self.p)
        return y
    
    def __str__(self) -> str:
        return f"x: {self.x}, \ny: {self.y}\n"
    
    def negative(self) -> "Point":
        return Point(self.curve, self.x, -self.y)
    
    #additionn operator override
    def __add__(self, other:"Point") -> "Point":
        return addition(self.curve, self, other)
    
    #substruction operator override
    def __sub__(self, other:"Point") -> "Point":
        return addition(self.curve,self, other.negative())
    
    #scalar multiplication operator override
    def __rmul__(self, k:int) -> "Point":
        return s_multiplication(self.curve, self, k)





def addition(curve: Curve, P: Point, Q: Point) -> Point:
    O = Point(curve, np.inf, np.inf)

    # O + P = P
    if P.x == O.x and P.y == O.y:
        return Q
    
    # P + O = P
    elif Q.x == O.x and Q.y == O.y:
        return P  

    # P + (-P) = O
    elif P.x == Q.x and P.y == -Q.y:
        return O

    # P + P = R
    elif P.x == Q.x and P.y == Q.y:  
        drv = ((3 * pow(P.x, 2) + curve.a) * pow(2 * P.y, -1, curve.p)) % curve.p
    else: 
        # P + Q = R
        drv = ((Q.y - P.y) * pow(Q.x - P.x, -1, curve.p)) % curve.p

    R_x = (pow(drv, 2) - P.x - Q.x) % curve.p
    R_y = (drv * (P.x - R_x) - P.y) % curve.p
    R = Point(curve, R_x, R_y)
    
    return R

    
def s_multiplication(curve: Curve, P: Point, k: int) -> Point: #double-and-add algorithm

    n = 1
    R = Point(curve, P.x, P.y)
    
    bin_k = ecc_math.binary(k)[1:]
    for bit in bin_k:
        if bit == 0:
            n *= 2
            R = addition(curve, R, R)   #double
        else:
            n *= 2
            R = addition(curve, R, R)   #double
            R = addition(curve,P,R)     #and add
            n += 1
            
    return R

# Embed the msg
def msg_to_points(curve:Curve, msg: str) -> list:
    int_msg_list = []
    
    for i in range(0, len(msg), bit_num):  # Divide by 8 for byte size
        msg_part_str = msg[i:i + (bit_num)]  # Adjusted for byte size
        msg_part_byte = bytes(msg_part_str.encode("utf-8"))
        
        int_msg_list.append(int.from_bytes(msg_part_byte, "big"))

    points = []
    
    for i in range(len(int_msg_list)):
        x_coordinate = int_msg_list[i]
        y_coordinate = Point.compute_y(curve,x_coordinate)   
        
        shift = 0 
        
        if y_coordinate == 0:
            while y_coordinate == 0:
            
                x_coordinate = x_coordinate + 1
                y_coordinate = Point.compute_y(curve, x_coordinate)
                
                shift += 1

        points.append(Point(curve, x_coordinate, y_coordinate, shift))  
        
    
    return points





def point_to_msg(points: list) -> str:
    int_msg = []
    for i in range(len(points)):
        int_msg_part = points[i].unshift
        
        int_msg.append(int_msg_part)
        
    msg = ""
    
    for x in int_msg:
        msg_part_byte = x.to_bytes((bit_num), "big")  # Adjusted for byte size
        
        # Decode only the relevant part of the byte array
        msg_part = msg_part_byte.decode("utf-8", errors='ignore').rstrip('\x00')  # Remove null bytes if any
        msg += msg_part

    return msg





P256 = Curve(
    a  = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc,
    b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
    p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff, # 2^256 − 2^224 + 2^192 + 2^96 − 1
    Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
    Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
)

secp256k1 = Curve(
    a  = 0x0,
    b  = 0x7,
    p  = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
    Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
)





