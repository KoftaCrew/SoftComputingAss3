from typing import Literal

TRI = "TRI"
TRAP = "TRAP"

class FuzzySet:
    def __init__(self, /, membershipFunction: Literal["TRI", "TRAP"], values: list[int], name="") -> None:
        self.name = name
        self.membershipFunction = membershipFunction
        self.values = values