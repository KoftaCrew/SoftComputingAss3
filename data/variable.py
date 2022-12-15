from .fuzzy_set import FuzzySet
from typing import Literal

IN = "IN"
OUT = "OUT"


class Variable:
    fuzzySets: list[FuzzySet]

    def __init__(self, type: Literal["IN", "OUT"], limits: tuple[int, int], name="") -> None:
        self.name = name
        self.fuzzySets = []
        self.type = type
        self.limits = limits
    
    def addFuzzySet(self, fuzzySet: FuzzySet):
        self.fuzzySets.append(fuzzySet)