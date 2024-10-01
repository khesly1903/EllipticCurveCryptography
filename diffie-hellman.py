import elliptic_curve as ec
import random
from typing import Tuple



class DiffieHellamn():
    def __init__(self, n:int, curve:ec.Curve):
        self.curve = curve
        self.P = curve.GPoint
        self.n = n

    @staticmethod
    def public_curve() -> ec.Curve:
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

        return curve

    @staticmethod
    def secret_n(curve:ec.Curve) -> int:
        print("\nEnter secret n (Empty for randomize): ")

        n = input("n: ")

        if n == "":
            print("Defaulting to random n.")
            n = random.randint(1, curve.p - 1)
            return n
        elif (int(n) > 0) & (int(n) < curve.p):
            return int(n)
        else:
            raise ValueError("Invalid n value.")


    @property
    def private_computation(self) -> str:
        if self.n < 0 & self.n > self.curve.p:
            raise ValueError("Invalid n value.")
        return (self.n * self.P).hex_merge_unshift
        

    def key_exchange(self, Q_:str) -> str:
        Q = self.curve.create_point_unshift(Q_)
        return (self.n * Q).hex_merge_unshift


#example usage
curve = DiffieHellamn.public_curve()

alice_secret_n = DiffieHellamn.secret_n(curve)
Alice = DiffieHellamn(alice_secret_n ,curve)
Alice_key = Alice.private_computation

bob_secret_n = DiffieHellamn.secret_n(curve)
Bob = DiffieHellamn(bob_secret_n, curve)
Bob_key = Bob.private_computation

key_Alice = Alice.key_exchange(Bob_key)
key_Bob = Bob.key_exchange(Alice_key)

if key_Alice == key_Bob:
    print(key_Alice)
else:
    raise ValueError("Keys do not match")
