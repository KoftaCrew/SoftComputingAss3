class Rule:
    def __init__(self, rule: str) -> None:
        # IN_variable set operator IN_variable set => OUT_variable set
        words = rule.split()

        if len(words) != 8:
            raise Exception("Invalid rule")

        self.inVariables = (words[0], words[3])
        self.inSets = (words[1], words[4])
        self.operator = words[2]
        self.outVariable = words[6]
        self.outSet = words[7]
