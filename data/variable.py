from .fuzzy_set import FuzzySet


class Variable:
    fuzzySets: list[FuzzySet]

    def __init__(self, name="") -> None:
        self.name = name
        self.fuzzySets = []
    
    def addFuzzySet(self, fuzzySet: FuzzySet):
        self.fuzzySets.append(fuzzySet)