import os
import sys
import copy
import random
import string

# Params
counter = 0
current_line = ''
input_file = '' # Input file
output_file = '' # Output file
program_stack = []
if_stack = []
key_words = ['if', 'else', 'for', 'var']

class Lexer:
    def __init__(self, text) -> None:
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in '0123456789':
                tokens.append(self.make_number())
            elif self.current_char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
                tokens.append(self.make_string())
            elif self.current_char in '!+-*/<==>=)(][}{':
                tokens.append(self.current_char)
                self.advance()
            else:
                tokens.append(self.current_char)
                self.advance()

        return tokens
    
    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in '.0123456789':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        
        if dot_count == 0: return int(num_str)
        else: return float(num_str)
    
    def make_string(self):
        string = ''

        while self.current_char != None and self.current_char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            string += self.current_char
            self.advance()
        
        return str(string)

def lexing(text):
    tokens = Lexer(text).make_tokens()
    return tokens

def write(content):
    global output_file
    with open(output_file, 'a') as f: f.write(str(content) + '\n')

def label_generator() -> str:
    return ''.join([random.choice(string.ascii_uppercase) for _ in range(10)])

def param_generator() -> str:
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(10)])

def condition_lexer(condition: str):
    condition = condition.replace(' ', '')
    result = []
    operation = ''
    if '>=' in condition:
        result = condition.split('>=')
        operation = '>='
    elif '<=' in condition:
        result = condition.split('<=')
        operation = '<='
    elif '==' in condition:
        result = condition.split('==')
        operation = '=='
    elif '!=' in condition:
        result = condition.split('!=')
        operation = '!='
    elif '>' in condition:
        result = condition.split('>')
        operation = '>'
    elif '<' in condition:
        result = condition.split('<')
        operation = '<'

    result.insert(0, operation)

    return result

class Checker:
    def __init__(self, input: str) -> None:
        self.input = input

    def isInt(self, exit=False):
        try:
            int(self.input)
        except:
            if exit: err(3, f'{self.input} is not an integer.')
            else: return False
        return True

    def isFloat(self, exit=False):
        try:
            float(self.input)
        except:
            if exit: err(3, f'{self.input} is not an float.')
            else: return False
        return True

    def isStr(self, exit=False):
        if self.input.count('\'') == 2 and self.input[0] == '\'' and self.input[-1] == '\'': return True
        else:
            if exit: err(3, f'{self.input} is not a string.')
            else: return False

    def isArray(self, exit=False):
        if self.input.count('[') + self.input.count(']') == 2 and self.input[0] == '[' and self.input[-1] == ']': return True
        else:
            if exit: err(3, f'{self.input} is not a array.')
            else: return False

    def isParam(self, exit=False):
        if self.isInt() or self.isFloat() or self.isStr() or self.input in key_words or self.input == '':
            if exit: err(3, f'{self.input} is not a param.', self.input)
            else: return False
        else: return True

    def getType(self, exit=True):
        if self.isInt(): return 'int'
        if self.isStr(): return 'str'
        if self.isFloat(): return 'float'
        if self.isParam(): return 'param'
        else:
            if exit: err(3, f'{self.input} is invald type.')
            else: return False

class Main:
    def __init__(self, input_file: str) -> None:
        global current_line
        self.program_stack = []
        self.if_stack = []
        self.counter = 0
        self.input_file = input_file

        input_ = open(self.input_file).read().replace(';', '\n').split('\n')
        input_ = [x for x in input_ if x != '']
        self.lines = {x: y.strip() for x, y in enumerate(input_)}

        while self.counter < len(self.lines):
            # Preprocessing
            current_line = self.lines[self.counter]
            comments = current_line.find('#')
            if comments != -1: current_line = current_line[:comments]
            current_line = current_line.strip()

            if current_line == '':
                self.counter += 1
                continue

            if current_line.startswith('var '): self._var(current_line)
            elif current_line.startswith('print'): self._print(current_line)
            elif current_line.startswith('if'): self._if(current_line)
            elif current_line.startswith('else'): self._else(current_line)
            elif current_line.startswith('for'): self._for(current_line)
            elif current_line.startswith('while'): self._while(current_line)
            elif current_line.startswith('cal'): self._cal(current_line)
            elif current_line == '}': self._endparen()

            self.counter += 1
    
    def _var(self, current_line: str):
        OBJCode = []
        parse_line = current_line[4:].strip()
        parse_line = parse_line.split('=')
        if len(parse_line) != 2: self.err(3, f'Expected 2 params, given {len(parse_line)}.')

        param = parse_line[0].strip()
        val = parse_line[1].strip()

        chk_param = Checker(param)
        chk_val = Checker(val)

        chk_param.isParam(exit=True)

        if chk_val.isArray():
            OBJCode += ['ARR']
            OBJCode += ['$' + param]
            temp_val = []
            for x in val[1:-1].split(','):
                x = x.strip()
                x_type = Checker(x).getType()
                if x_type == 'param': x = '$' + x
                temp_val.append(x)
            temp_val = ', '.join(temp_val)
            OBJCode += [temp_val]
        else:
            OBJCode += ['VAL']
            OBJCode += ['$' + param]
            OBJCode += [('$' if chk_val.isParam(exit=False) else '') + val]

        write(' '.join(OBJCode))
    
    def _print(self, current_line: str):
        parse_line = current_line[5:].strip()
        if parse_line[0] != '(' or parse_line[-1] != ')': self.err(3, f'Perhaps you forgot a paren.')
        parse_line = parse_line[1:-1]
        parse_line = parse_line.split(',')
        for printl in parse_line:
            printl = printl.strip()
            chk_printl = Checker(printl)
            if chk_printl.isStr() or chk_printl.isInt() or chk_printl.isFloat(): write('MSG ' + printl)
            elif chk_printl.isParam(): write('MSG $' + printl)

    def _if(self, current_line: str):
        parse_line = current_line[2:].strip()
        if parse_line[0] != '(' or parse_line[-2] != ')' or parse_line[-1] != '{': self.err(3, f'Perhaps you forgot a paren.')
        condition = parse_line[1:-2]
        condition = condition_lexer(condition)
        self.if_stack = copy.deepcopy(condition)

        LABEL = label_generator()

        chk_condition1 = Checker(condition[1])
        chk_condition2 = Checker(condition[2])

        if chk_condition1.isParam(): condition[1] = "$" + condition[1]
        elif chk_condition1.isInt(): condition[1] = int(condition[1])
        elif chk_condition1.isFloat(): condition[1] = float(condition[1])

        if chk_condition2.isParam(): condition[2] = "$" + condition[2]
        elif chk_condition2.isInt(): condition[2] = int(condition[2])
        elif chk_condition2.isFloat(): condition[2] = float(condition[2])

        if condition[0] == '<': write(f'JLE {condition[2]} {condition[1]} {LABEL}')
        elif condition[0] == '>': write(f'JLE {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '<=': write(f'JLT {condition[2]} {condition[1]} {LABEL}')
        elif condition[0] == '>=': write(f'JLT {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '==': write(f'JNQ {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '!=': write(f'JEQ {condition[1]} {condition[2]} {LABEL}')

        self.program_stack.append(f'LAB {LABEL}')
    
    def _else(self, current_line: str):
        parse_line = current_line[4:].strip()
        if parse_line[0] != '{': self.err(3, f'Perhaps you forgot a paren.')
        if len(self.if_stack) == 0: self.err(3, f'Perhaps you forgot a if().')
        condition = self.if_stack
        self.if_stack = []

        LABEL = label_generator()

        chk_condition1 = Checker(condition[1])
        chk_condition2 = Checker(condition[2])

        if chk_condition1.isParam(): condition[1] = "$" + condition[1]
        elif chk_condition1.isInt(): condition[1] = int(condition[1])
        elif chk_condition1.isFloat(): condition[1] = float(condition[1])

        if chk_condition2.isParam(): condition[2] = "$" + condition[2]
        elif chk_condition2.isInt(): condition[2] = int(condition[2])
        elif chk_condition2.isFloat(): condition[2] = float(condition[2])

        if condition[0] == '<': write(f'JLT {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '>': write(f'JLT {condition[2]} {condition[1]} {LABEL}')
        elif condition[0] == '<=': write(f'JLE {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '>=': write(f'JLE {condition[2]} {condition[1]} {LABEL}')
        elif condition[0] == '==': write(f'JEQ {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '!=': write(f'JNQ {condition[1]} {condition[2]} {LABEL}')

        self.program_stack.append(f'LAB {LABEL}')
    
    def _for(self, current_line: str):
        parse_line = current_line[3:].strip()
        if parse_line[0] != '(' or parse_line[-2] != ')' or parse_line[-1] != '{': self.err(3, f'Perhaps you forgot a paren.')
        parse_line = parse_line[1:-2]
        parse_line = parse_line.split(',')
        if len(parse_line) != 3: self.err(3, f'Perhaps you forgot a condition.')

        LABEL = label_generator()

        temp_stack = []
        initial, condition, operation = parse_line
        self._var(initial)

        write(f'LAB {LABEL}')

        # Condition
        condition = condition_lexer(condition)

        operation = self._cal(operation)
        temp_stack.append(operation)

        chk_condition1 = Checker(condition[1])
        chk_condition2 = Checker(condition[2])

        if chk_condition1.isParam(): condition[1] = "$" + condition[1]
        elif chk_condition1.isInt(): condition[1] = int(condition[1])
        elif chk_condition1.isFloat(): condition[1] = float(condition[1])

        if chk_condition2.isParam(): condition[2] = "$" + condition[2]
        elif chk_condition2.isInt(): condition[2] = int(condition[2])
        elif chk_condition2.isFloat(): condition[2] = float(condition[2])

        if condition[0] == '<': temp_stack.append(f'JLT {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '>': temp_stack.append(f'JLT {condition[2]} {condition[1]} {LABEL}')
        elif condition[0] == '<=': temp_stack.append(f'JLE {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '>=': temp_stack.append(f'JLE {condition[2]} {condition[1]} {LABEL}')
        elif condition[0] == '==': temp_stack.append(f'JEQ {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '!=': temp_stack.append(f'JNQ {condition[1]} {condition[2]} {LABEL}')

        self.program_stack.append(temp_stack)
    
    def _while(self, current_line: str):
        parse_line = current_line[5:].strip()
        if parse_line[0] != '(' or parse_line[-2] != ')' or parse_line[-1] != '{': self.err(3, f'Perhaps you forgot a paren.')
        condition = parse_line[1:-2]

        LABEL = label_generator()

        temp_stack = []

        write(f'LAB {LABEL}')

        # Condition
        condition = condition_lexer(condition)

        chk_condition1 = Checker(condition[1])
        chk_condition2 = Checker(condition[2])

        if chk_condition1.isParam(): condition[1] = "$" + condition[1]
        elif chk_condition1.isInt(): condition[1] = int(condition[1])
        elif chk_condition1.isFloat(): condition[1] = float(condition[1])

        if chk_condition2.isParam(): condition[2] = "$" + condition[2]
        elif chk_condition2.isInt(): condition[2] = int(condition[2])
        elif chk_condition2.isFloat(): condition[2] = float(condition[2])

        if condition[0] == '<': temp_stack.append(f'JLT {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '>': temp_stack.append(f'JLT {condition[2]} {condition[1]} {LABEL}')
        elif condition[0] == '<=': temp_stack.append(f'JLE {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '>=': temp_stack.append(f'JLE {condition[2]} {condition[1]} {LABEL}')
        elif condition[0] == '==': temp_stack.append(f'JEQ {condition[1]} {condition[2]} {LABEL}')
        elif condition[0] == '!=': temp_stack.append(f'JNQ {condition[1]} {condition[2]} {LABEL}')

        self.program_stack.append(temp_stack)
    
    def _endparen(self):
        if len(self.program_stack) == 0: self.err(2, f'Perhaps you forgot a paren.')
        line = self.program_stack.pop()
        line_type = type(line)
        if line_type == str: write(line)
        if line_type == list:
            for i in line:
                write(i)
    
    def _cal(self, current_line: str, write_=True):
        parse_line = current_line.replace(' ', '')[3:]

        if '+=' in parse_line:
            par1, par2 = parse_line.split('+=')
            chk_par1 = Checker(par1)
            chk_par1.isParam(exit=True)
            if write_: write(f'ADD ${par1} {par2}')
            else: return f'ADD ${par1} {par2}'
        elif '-=' in parse_line:
            par1, par2 = parse_line.split('-=')
            chk_par1 = Checker(par1)
            chk_par1.isParam(exit=True)
            if write_: write(f'SUB ${par1} {par2}')
            else: return f'SUB ${par1} {par2}'
        elif '*=' in parse_line:
            par1, par2 = parse_line.split('*=')
            chk_par1 = Checker(par1)
            chk_par1.isParam(exit=True)
            if write_: write(f'MUL ${par1} {par2}')
            else: return f'MUL ${par1} {par2}'
        elif '/=' in parse_line:
            par1, par2 = parse_line.split('/=')
            chk_par1 = Checker(par1)
            chk_par1.isParam(exit=True)
            if write_: write(f'DIV ${par1} {par2}')
            else: return f'DIV ${par1} {par2}'
        elif '=' in parse_line:
            par1, par2 = parse_line.split('=')
            chk_par1 = Checker(par1)

            chk_par1.isParam(exit=True)
            PARAM = param_generator()
            OP = ''
            if '+' in par2:
                par2 = par2.split('+')
                OP = 'ADD'
            elif '-' in par2:
                    par2 = par2.split('-')
                    OP = 'SUB'
            elif '*' in par2:
                    par2 = par2.split('*')
                    OP = 'MUL'
            elif '/' in par2:
                    par2 = par2.split('/')
                    OP = 'DIV'

            o1, o2 = par2
            chk_o1 = Checker(o1)
            chk_o2 = Checker(o2)

            if chk_o1.isParam(): o1 = "$" + o1
            elif chk_o1.isInt(): o1 = int(o1)
            elif chk_o1.isFloat(): o1 = float(o1)

            if chk_o2.isParam(): o2 = "$" + o2
            elif chk_o2.isInt(): o2 = int(o2)
            elif chk_o2.isFloat(): o2 = float(o2)

            if write_:
                write(f'VAL ${PARAM} {o1}')
                write(f'{OP} ${PARAM} {o2}')
                write(f'VAL ${par1} ${PARAM}')
            else:
                return [f'VAL ${PARAM} {o1}', f'{OP} ${PARAM} {o2}', f'VAL ${par1} ${PARAM}']

    def err(self, code: int, msg: str, error='') -> None:
        codes = {
            0: "Input Error",
            1: "Undefined",
            2: "Syntax Error",
            3: "Type Error",
            4: "Register Error",
            5: "Invalid Method Error"
        }

        if error != '': pointer = ' ' * current_line.find(error) + '^' * len(error)
        else: pointer = '    ^^^'

        print(f'Traceback:\
            \n  File {self.input_file}, line {counter}\
            \n    {current_line}\
            \n    {pointer}\
            \n{codes[code]}: {msg}')
        exit()

def err(code: int, msg: str, error='') -> None:
    global current_line, input_file

    codes = {
        0: "Input Error",
        1: "Undefined",
        2: "Syntax Error",
        3: "Type Error",
        4: "Register Error",
        5: "Invalid Method Error"
    }

    if error != '': pointer = ' ' * current_line.find(error) + '^' * len(error)
    else: pointer = '    ^^^'

    print(f'Traceback:\
          \n  File {input_file}, line {counter}\
          \n    {current_line}\
          \n    {pointer}\
          \n{codes[code]}: {msg}')
    exit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Input Error: Input file is not specified.')
        exit()
    if len(sys.argv) < 3:
        print('Input Error: Output file is not specified.')
        exit()

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(input_file): err(0, 'Input file not exists.')
    with open(output_file, 'w') as f: f.write('') # Clear output file

    Main(input_file)