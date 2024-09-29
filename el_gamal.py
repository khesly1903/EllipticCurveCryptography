import elliptic_curve as ec  
import random
from typing import Tuple

class ElGamal:
    def __init__(self, curve):
        self.curve = curve
        self.P = curve.GPoint

    @staticmethod
    def public_parameters() -> Tuple[ec.Curve, int]:
        print("Select an elliptic curve (Empty for default)")
        print("    1. P256")
        print("    2. secp256k1")
        print("    3. P521")

        curve_choice = input("Choice: ")

        if curve_choice == "1":
            curve = ec.P256
        elif curve_choice == "2":
            curve = ec.secp256k1
        elif curve_choice == "3":
            curve = ec.P521
        else:
            curve = ec.P256
            print("Defaulting to P-256.")

        print("\nEnter secret n (Empty for randomize): ")

        n_input = input("n: ")

        if n_input == "":
            print("Defaulting to random n.")
            n = random.randint(1, curve.p - 1)
            print(f"n: {n}\n")
        elif (int(n_input) > 0) & (int(n_input) < curve.p):
            n = int(n_input)
        else:
            raise ValueError("Invalid n value.")

        return (curve, n)

    def key(self, n: int) -> str:
        key_point = ec.s_multiplication(self.curve, self.P, n)
        return key_point.hex_merge

    def encryption(self, keyQ: str, msg: str) -> str:
        keyQ = self.curve.create_point(keyQ)

        msg_points = ec.msg_to_points(self.curve, msg)

        k = random.randint(1, self.curve.p - 1)
        c_1 = (k * self.P).hex_merge

        encrypted = ""

        for i in range(len(msg_points)):
            c_2_point = msg_points[i] + (k * keyQ)
            c_2_point.set_slient_shift(msg_points[i].get_shift)
            c_2 = c_2_point.hex_merge

            encrypted += c_1 + c_2

        return encrypted

    def decryption(self, n: int, encrypted: str) -> str:
        coordinate_size = (self.curve.p.bit_length() + 7) // 8
        shift_size = 2
        point_size = 2 * coordinate_size + 2 * shift_size
        point_hex_length = point_size * 2


        points = []

        for i in range(0, len(encrypted), 2 * point_hex_length):
            c_1_hex = encrypted[i:i + point_hex_length]
            c_2_hex = encrypted[i + point_hex_length:i + 2 * point_hex_length]

            c_1 = self.curve.create_point(c_1_hex)
            c_2 = self.curve.create_point(c_2_hex)

            m = c_2 - (n * c_1)
            m.set_shift(c_2.get_slient_shift)

            points.append(m)

        decrypted = ec.point_to_msg(points)

        return decrypted



# Sample usage
msg = "Mustafa Kemal Ataturk was the founder and first president of the Republic of Turkey, leading the Turkish nation to freedom."

curve, n = ElGamal.public_parameters()

eg = ElGamal(curve)

keyQ = eg.key(n)

enc = eg.encryption(keyQ, msg)
print(f"\n  Encrypted message\n\n{enc}")

dec = eg.decryption(n, enc)
print(f"\n  Decrypted message\n\n{dec}")




