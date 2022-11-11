import os
import sys

# Params
params = {}
register = {'A': None}
counter = 0
current_line = ''
file = ''

class Checker:
    def __init__(self, input: str) -> None:
        self.input = input

    # Return False is input not in params or not a number
    def defined(self, exit=True):
        if self.isnum(exit=False) or self.isstr(exit=False): return True
        if self.input not in params:
            if exit: err(1, f'{self.input} is not defined.')
            else: return False
        return True

    # Return False if input has already been defined
    def undefined(self, exit=True):
        if self.input in params:
            if exit: err(5, f'{self.input} has already been defined.')
            else: return False
        return True

    # Return False if input is number
    def isnum(self, exit=True):
        try:
            int(self.input)
        except:
            if exit: err(3, f'{self.input} must be a number.')
            else: return False
        return True

    # Return True if input is number
    def notnum(self, exit=True):
        if self.isnum(exit=False):
            if exit: err(3, f'{self.input} can not be a number.')
            else: return False
        return True
    
    def isstr(self, exit=True):
        if self.input.count('\'') == 2 and self.input[0] == '\'' and self.input[-1] == '\'':
            return True
        else:
            if exit: err(3, f'{self.input} is not a string.')
            else: return False
    
    def notstr(self, exit=True):
        if self.isstr(exit=False):
            if exit: err(3, f'{self.input} can not be a string.')
            else: return False
        return True

class Operation:
    def __init__(self, content: str) -> None:
        self.content = content

    def val(self):
        par1, par2 = self.content.split(' ')
        chk1 = Checker(par1)
        chk2 = Checker(par2)

        chk1.notnum()
        chk1.notstr()
        chk2.defined()

        if chk2.isnum(exit=False):
            params[par1] = {'type': 'int', 'val': int(par2)}
        elif chk2.isstr(exit=False):
            params[par1] = {'type': 'str', 'val': par2[1:-1]}
        else:
            params[par1] = params[par2]
        print(params)

    def add(self):
        par1, par2 = self.content.split(' ')
        chk2 = Checker(par2)
        chk2.defined()

        if params[par1]['type'] == params[par2]['type']:
            params[par1]['val'] += params[par2]['val'] if chk2.defined(exit=False) else par2
        else:
            err(3, f'Type of {par1} and {par2} are not matched.')

    def sub(self):
        par1, par2 = self.content.split(' ')
        chk2 = Checker(par2)
        chk2.defined()

        if params[par1]['type'] == params[par2]['type']:
            params[par1]['val'] -= params[par2]['val'] if chk2.defined(exit=False) else par2
        else:
            err(3, f'Type of {par1} and {par2} are not matched.')

    def mul(self):
        par1, par2 = self.content.split(' ')
        chk1 = Checker(par1)
        chk2 = Checker(par2)

        chk1.notnum()
        chk1.defined()
        chk2.defined()
        
        params[par1] *= int(par2) if chk2.isnum(exit=False) else params[par2]

    def div(self):
        par1, par2 = self.content.split(' ')
        chk1 = Checker(par1)
        chk2 = Checker(par2)

        chk1.isnum()
        chk1.defined()
        chk2.defined()

        params[par1] /= int(par2) if chk2.isnum(exit=False) else params[par2]
    
    def jmp(self):
        global counter
        to = self.content
        chk = Checker(to)

        chk.defined()

        if chk.isnum(exit=False):
            if int(to) < 1: err(2, f'Cannot jump to address {to}.')
            else: counter = int(to) - 2
        else:
            if int(params[to]) < 1: err(2, f'Cannot jump to address {params[to]}.')
            else: counter = int(params[to]) - 2
    
    def lda(self):
        global register
        chk = Checker(self.content)

        if chk.isstr(exit=False):
            register['A'] = self.content[1:-1]
        elif chk.isnum(exit=False):
            register['A'] = int(self.content)
        else:
            chk.defined()
            register['A'] = params[self.content]
    
    def sta(self):
        global register
        chk = Checker(self.content)

        chk.notnum()
        chk.notstr()
        chk.defined()

        if register['A'] == None: err(4, f'Register A has not been assigned.')
        else: params[self.content] = register['A']
    
    def lab(self):
        global counter
        chk = Checker(self.content)

        chk.notnum()
        chk.notstr()

        params[self.content] = counter

    def msg(self):
        chk = Checker(self.content)

        chk.defined()

        if chk.isnum(exit=False): print(self.content)
        elif chk.isstr(exit=False): print(self.content[1:-1])
        else: print(params[self.content])

def err(code: int, msg: str) -> None:
    global current_line, file

    codes = {
        0: "Input Error",
        1: "Undefined",
        2: "Syntax Error",
        3: "Type Error",
        4: "Register Error",
        5: "Defined"
    }

    print(f'Traceback:\
          \n  File {file}, line {counter}\
          \n    {current_line}\
          \n      ^^^\
          \n{codes[code]}: {msg}')
    exit()

def main(input: str) -> None:
    global counter, current_line
    lines = {x: y for x, y in enumerate(open(input))}

    while counter < len(lines):
        current_line = lines[counter].replace('\n', '')

        if current_line == '':
            counter += 1
            continue

        try:
            op, content = current_line.split(' ', 1)
            op.upper()
            opIns = Operation(content)
        except:
            op = current_line

        match op:
            case 'VAL': opIns.val()
            case 'ADD': opIns.add()
            case 'SUB': opIns.sub()
            case 'MUL': opIns.mul()
            case 'DIV': opIns.div()
            case 'MSG': opIns.msg()
            case 'JMP': opIns.jmp()
            case 'LDA': opIns.lda()
            case 'LAB': opIns.lab()
            case 'END': exit()
        
        counter += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Input Error: Input file not specified.')
        exit()

    input = sys.argv[1]
    if not os.path.isfile(input): err(0, 'Input file not exists.')

    file = input
    main(input)