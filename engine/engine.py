from data.fuzzy_set import TRI
from data.rule import Rule
from data.variable import IN, OUT, Variable

def getIntercept(shape: list[float], values: list[float], x: float) -> float:
    if x <= shape[0]:
        return values[0]
    
    if x >= shape[-1]:
        return values[-1]

    for i in range(len(shape) - 1):
        if x >= shape[i] and x <= shape[i + 1]:
            return values[i] + (x - shape[i]) * (values[i + 1] - values[i]) / (shape[i + 1] - shape[i])

def fuzzify(variables: list[Variable], input: list[float]) -> list[list[float]]:
    result = []

    for i, variable in enumerate(variables):
        membership = []
        for set in variable.fuzzySets:
            membership.append(getIntercept(set.values, [0, 1, 0] if set.type == TRI else [0, 1, 1, 0], input[i]))

        result.append(membership)

    return result

def inference(rules: list[Rule], fuzzyInputs: list[list[float]], inVariables: list[Variable], outVariables: list[Variable]) -> list[list[float]]:
    result = []
    for variable in outVariables:
        result.append([0] * len(variable.fuzzySets))

    for rule in rules:
        # Get the index of the input and output variables by checking the name of the variable
        inIndex1 = [i for i, x in enumerate(inVariables) if x.name == rule.inVariables[0]][0]
        inIndex2 = [i for i, x in enumerate(inVariables) if x.name == rule.inVariables[1]][0]
        outIndex = [i for i, x in enumerate(outVariables) if x.name == rule.outVariable][0]

        inSetIndices = [i for i, x in enumerate(inVariables[inIndex1].fuzzySets)
                         if x.name == rule.inSets[0]] + [i for i, x in enumerate(inVariables[inIndex2].fuzzySets) 
                         if x.name == rule.inSets[1]]
        outSetIndex = [i for i, x in enumerate(outVariables[outIndex].fuzzySets) if x.name == rule.outSet][0]

        if rule.operator == "and":
            output = min(fuzzyInputs[inIndex1][inSetIndices[0]], fuzzyInputs[inIndex2][inSetIndices[1]])
        elif rule.operator == "or":
            output = max(fuzzyInputs[inIndex1][inSetIndices[0]], fuzzyInputs[inIndex2][inSetIndices[1]])
        elif rule.operator == "and_not":
            output = min(fuzzyInputs[inIndex1][inSetIndices[0]], 1 - fuzzyInputs[inIndex2][inSetIndices[1]])
        elif rule.operator == "or_not":
            output = max(fuzzyInputs[inIndex1][inSetIndices[0]], 1 - fuzzyInputs[inIndex2][inSetIndices[1]])

        result[outIndex][outSetIndex] = max(result[outIndex][outSetIndex], output)

    return result

def defuzzify(variables: list[Variable], fuzzyOutputs: list[list[float]]) -> list[tuple[float, str]]:
    result = []
    dominantSet = []

    for i, variable in enumerate(variables):
        result.append(0)
        for j, set in enumerate(variable.fuzzySets):
            result[i] += set.getCentroid() * fuzzyOutputs[i][j]
        result[i] /= sum(fuzzyOutputs[i])
        dominantSet.append(variable.fuzzySets[fuzzyOutputs[i].index(max(fuzzyOutputs[i]))].name)

    return list(zip(result, dominantSet))

def simulate(variables: list[Variable], input: list[float], rules: list[str]) -> list[tuple[float, str]]:
    inVariables = [x for x in variables if x.type == IN]
    outVariables = [x for x in variables if x.type == OUT]
    rules = [Rule(x) for x in rules]

    fuzzyInputs = fuzzify(inVariables, input)
    fuzzyOutputs = inference(rules, fuzzyInputs, inVariables, outVariables)
    crispOutputs = defuzzify(outVariables, fuzzyOutputs)

    return crispOutputs
