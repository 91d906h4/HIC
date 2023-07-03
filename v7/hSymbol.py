class Symbol:
    def __init__(self) -> None:
        pass

    def getWeight(self, token: str) -> int:
        weight = {
            '**': 0,
            '++': 1,
            '*': 2,
            '/': 2,
            '%': 3,
            '+': 4,
            '-': 4,
            '<<': 5,
            '>>': 5,
            '<': 6,
            '>': 6,
            '<=': 6,
            '>=': 6,
            '==': 6,
            '!=': 6,
            '&': 7,
            '^': 7,
            '|': 7,
            'not': 8,
            'and': 8,
            'or': 8
        }

        if token not in weight: return -1
        else: return weight[token]

    def lists(self) -> list:
        return [
            '**',
            '++',
            '*',
            '/',
            '%',
            '+',
            '-',
            '<<',
            '>>',
            '<',
            '>',
            '<=',
            '>=',
            '==',
            '!=',
            '&',
            '^',
            '|',
            'not',
            'and',
            'or'
        ]