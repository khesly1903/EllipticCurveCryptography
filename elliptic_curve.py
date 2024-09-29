import numpy as np
import ecc_math

bit_num = 32

class Curve:
    def __init__(self, a: int, b: int, p: int, name: str, Gx: int, Gy: int, msg_length: int):
        self.a = a
        self.b = b
        self.p = p
        self.Gx = Gx
        self.Gy = Gy
        self.name = name
        self.msg_length = msg_length

        # Non-singularity test
        if (4 * pow(self.a, 3) + 27 * pow(self.b, 2)) % self.p == 0:
            raise ValueError("Curve is singular")

    #generator point of curve
    @property
    def GPoint(self) -> "Point":
        return Point(self, self.Gx, self.Gy)
    
    def __str__(self):
        return f"{self.name}"
    
    #for given hex value (eg. encrypted message) it creates point
    #slient shift is for transporing the shift value of c_2
    #   when message decoding, the m point has shift 0
    #   because of mathematics the m is same but shift will not
    #   to keep the shift of m, just embed in the c_2
    def create_point(self, hex_point: str) -> "Point":
        msg = bytes.fromhex(hex_point)

        length = (self.p.bit_length() + 7) // 8
        shift_size = 2

        x_bytes = msg[:length]
        shift_bytes = msg[length:length + shift_size]
        slient_shift_bytes = msg[length + shift_size:length + 2 * shift_size]
        y_bytes = msg[-length:]

        x = int.from_bytes(x_bytes, 'big')
        shift = int.from_bytes(shift_bytes, 'big')
        slient_shift = int.from_bytes(slient_shift_bytes, 'big')
        y = int.from_bytes(y_bytes, 'big')

        return Point(self, x, y, shift, slient_shift)



class Point:
    def __init__(self, curve: Curve, x: int, y: int, shift: int = 0, slient_shift: int = 0):
        self.curve = curve
        self._x = x
        self._y = y
        self.shift = shift
        self.slient_shift = slient_shift

        #check that if it is non-singular or not
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

    @property
    def get_slient_shift(self) -> int:
        return self.slient_shift

    @property
    def get_coordinates(self) -> tuple:
        return (self.x, self.y)


    #embedded points are sended this way 
    #   (actually i send this way there is some hashing algorithms
    #   to embed the encryped points
    #   https://www.ietf.org/archive/id/draft-irtf-cfrg-hash-to-curve-10.html)
    @property
    def hex_merge(self) -> str:
        coordinate_size = (self.curve.p.bit_length() + 7) // 8
        shift_size = 2

        x_bytes = self.x.to_bytes(coordinate_size, 'big')
        y_bytes = self.y.to_bytes(coordinate_size, 'big')
        shift_bytes = self.shift.to_bytes(shift_size, 'big')
        slient_shift_bytes = self.slient_shift.to_bytes(shift_size, 'big')

        merged_bytes = x_bytes + shift_bytes + slient_shift_bytes + y_bytes
        return merged_bytes.hex()

    def set_shift(self, shift: int) -> "Point":
        self.shift = shift
        return self

    def set_slient_shift(self, slient_shift: int) -> "Point":
        self.slient_shift = slient_shift
        return self

    def get_msg(self, shift: int) -> int:
        return self.x - shift

    @staticmethod
    #https://github.com/lc6chang/ecc-pycrypto/blob/master/ecc/math_utils/mod_sqrt.py()
    def compute_y(curve: Curve, x: int) -> int:
        right = (x * x * x + curve.a * x + curve.b) % curve.p
        y = ecc_math.modsqrt(right, curve.p)
        return y

    def __str__(self) -> str:
        return f"x: {self.x}, \ny: {self.y}\n"

    def negative(self) -> "Point":
        return Point(self.curve, self.x, -self.y % self.curve.p)

    def __add__(self, other: "Point") -> "Point":
        return addition(self.curve, self, other)

    def __sub__(self, other: "Point") -> "Point":
        return addition(self.curve, self, other.negative())

    def __rmul__(self, k: int) -> "Point":
        return s_multiplication(self.curve, self, k)


def addition(curve: Curve, P: Point, Q: Point) -> Point:
    O = Point(curve, np.inf, np.inf)

    # O + P = P
    if P.x == np.inf and P.y == np.inf:
        return Q

    # P + O = P
    elif Q.x == np.inf and Q.y == np.inf:
        return P

    # P + (-P) = O
    elif P.x == Q.x and (P.y + Q.y) % curve.p == 0:
        return O

    # P + P = R
    elif P.x == Q.x and P.y == Q.y:
        s = (3 * P.x * P.x + curve.a) * pow(2 * P.y, -1, curve.p)
    else:
        s = (Q.y - P.y) * pow(Q.x - P.x, -1, curve.p)

    s = s % curve.p
    R_x = (s * s - P.x - Q.x) % curve.p
    R_y = (s * (P.x - R_x) - P.y) % curve.p
    R = Point(curve, R_x, R_y)

    return R

#double and add algorithm
def s_multiplication(curve: Curve, P: Point, k: int) -> Point:
    N = P
    Q = None  # Point at infinity

    for i in reversed(bin(k)[2:]):
        if i == '1':
            if Q is None:
                Q = N       #double
            else:
                Q = Q + N   #double and add
        N = N + N

    return Q



#string message to elliptic curve points
#bit_num slices the message to smaller pieces
def msg_to_points(curve: Curve, msg: str) -> list:
    int_msg_list = []

    for i in range(0, len(msg), bit_num):
        msg_part_str = msg[i:i + bit_num]
        msg_part_byte = bytes(msg_part_str, "utf-8")
        int_msg_list.append(int.from_bytes(msg_part_byte, "big"))

    points = []

    for x_coordinate in int_msg_list:
        y_coordinate = Point.compute_y(curve, x_coordinate)

        shift = 0

        if y_coordinate == 0:
            while y_coordinate == 0:
                x_coordinate += 1
                y_coordinate = Point.compute_y(curve, x_coordinate)
                shift += 1

        points.append(Point(curve, x_coordinate, y_coordinate, shift))


    return points



#elliptic curve points to string message
def point_to_msg(points: list) -> str:
    int_msg = []

    for point in points:
        int_msg_part = point.unshift
        int_msg.append(int_msg_part)

    msg = b""

    for x in int_msg:
        byte_size = (x.bit_length() + 7) // 8
        if byte_size > 0:
            msg_part_byte = x.to_bytes(byte_size, "big")
            msg += msg_part_byte

    return msg.decode("utf-8", errors='ignore').rstrip('\x00')


#some well known short weierstrass elliptic curves
#msg_length is smaller pieces messages lengths
#   it changes when bit_num changes, default bit_num is 32
#   and it depends on the length of prime

P256 = Curve(
    a  = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc,
    b  = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
    p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
    name = "P256",
    Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
    Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5,
    msg_length = 536
)

secp256k1 = Curve(
    a  = 0x0,
    b  = 0x7,
    p  = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
    name = "secp256k1",
    Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8,
    msg_length = 536
)

P521 = Curve(
    a = 0x01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc,
    b = 0x0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00,
    p = 0x01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff,
    name = "P521",
    Gx = 0x00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66,
    Gy = 0x011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650,
    msg_length = 1060
)
