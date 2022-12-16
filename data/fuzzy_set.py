from typing import Literal

TRI = "TRI"
TRAP = "TRAP"


class FuzzySet:
    def __init__(self, /, type: Literal["TRI", "TRAP"], values: list[int], name="") -> None:
        self.name = name
        self.type = type
        self.values = values
