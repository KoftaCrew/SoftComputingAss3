from typing import Literal

TRI = "TRI"
TRAP = "TRAP"


class FuzzySet:
    def __init__(self, /, type: Literal["TRI", "TRAP"], values: list[int], name="") -> None:
        self.name = name
        self.type = type
        self.values = values

    def getCentroid(self) -> float:
        if self.type == TRI:
            return sum(self.values) / 3
        elif self.type == TRAP:
            # The centroid of a non-self-intersecting closed polygon
            y = [0, 1, 1, 0]
            a = 0
            for i in range(3):
                a += (self.values[i] * y[i + 1]) - (self.values[i + 1] * y[i])
            a /= 2

            cx = 0
            for i in range(3):
                cx += (self.values[i] + self.values[i + 1]) * (self.values[i] * y[i + 1] - self.values[i + 1] * y[i])
            
            return cx / (6 * a)
