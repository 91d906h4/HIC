import os
import sys
import random
import string

# Params
counter = 0
current_line = ''
file = ''
output = ''
temp_stack = []

class Checker:
    def __init__(self, input) -> None:
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
        if self.isInt() or self.isFloat() or self.isStr() or self.input == '':
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

def conditionParser(condition: str):
    for i in ['<', '>', '<=', '>=', '==', '!=']:
        if i in condition:
            condition = condition.split(i)
            condition.insert(0, i)
            condition = [x.strip() for x in condition]
            break
    return condition

def workParser(work: str):
    for i in ['+=', '-=', '*=', '/=', '+', '-', '*', '/']:
        if i in work:
            work = work.split(i)
            work.insert(0, i)
            work = [x.strip() for x in work]
            break
    return work

def write(content):
    global output
    with open(output, 'a') as f: f.write(str(content) + '\n')

def main(input: str) -> None:
    global counter, current_line
    lines = {x: y for x, y in enumerate(open(input))}

    while counter < len(lines):
        # Preprocessing
        current_line = lines[counter].replace('\n', '')
        comments = current_line.find('#')
        if comments != -1: current_line = current_line[:comments]
        current_line = current_line.strip()

        if current_line == '':
            counter += 1
            continue

        OBJCode = []
        if current_line.startswith('var '):
            parse_line = current_line[4:].strip()
            parse_line = parse_line.split('=')
            if len(parse_line) != 2: err(3, f'Expected 2 params, given {len(parse_line)}.')

            param = parse_line[0].strip()
            val = parse_line[1].strip()

            chk_param = Checker(param)
            chk_val = Checker(val)

            chk_param.isParam()

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

        elif current_line.startswith('print'):
            parse_line = current_line[5:].strip()
            if parse_line[0] != '(' or parse_line[-1] != ')': err(3, f'Function print().')
            parse_line = parse_line[1:-1]
            parse_line = parse_line.split(',')
            for printl in parse_line:
                printl = printl.strip()
                chk_printl = Checker(printl)
                if chk_printl.isStr(): write('MSG ' + printl)
                elif chk_printl.isParam(): write('MSG $' + printl)

        elif current_line.startswith('for'):
            parse_line = current_line[3:].strip()
            if parse_line[0] != '(' or parse_line[-1] != ')': err(3, f'Function for().')
            parse_line = parse_line[1:-1]
            parse_line = parse_line.split(';')
            if len(parse_line) != 2: err(3, f'Function for().')

            LABEL = ''.join([random.choice(string.ascii_uppercase) for i in range(10)])
            write(f'LAB {LABEL}')

            condition, work = parse_line
            condition = conditionParser(condition)

            chk_condition1 = Checker(condition[1])
            chk_condition2 = Checker(condition[2])

            if chk_condition1.isParam(exit=True): condition[1] = "$" + condition[1]
            if chk_condition2.isParam(): condition[2] = "$" + condition[2]

            if condition[0] == '<': temp_stack.append(f'JLT {condition[1]} {condition[2]} {LABEL}')
            elif condition[0] == '>': temp_stack.append(f'JLT {condition[2]} {condition[1]} {LABEL}')

            work = workParser(work)

            chk_work1 = Checker(work[1])
            chk_work2 = Checker(work[2])

            dict1 = {'+=': 'ADD', '-=': 'SUB', '*=': 'MUL', '/=': "DIV"}
            if work[0] in dict1:
                if chk_work1.isParam(exit=True): work[1] = "$" + work[1]
                if chk_work2.isParam(): work[2] = "$" + work[2]
                temp_stack.append(f'{dict1[work[0]]} {work[1]} {work[2]}')
        
        elif current_line == 'endfor':
            write(temp_stack.pop())
            write(temp_stack.pop())
        
        elif current_line.startswith('if'):
            parse_line = current_line[2:].strip()
            if parse_line[0] != '(' or parse_line[-1] != ')': err(3, f'Function if().')
            parse_line = parse_line[1:-1]

            LABEL = ''.join([random.choice(string.ascii_uppercase) for i in range(10)])

            condition = conditionParser(parse_line)

            chk_condition1 = Checker(condition[1])
            chk_condition2 = Checker(condition[2])

            if chk_condition1.isParam(exit=True): condition[1] = "$" + condition[1]
            if chk_condition2.isParam(): condition[2] = "$" + condition[2]

            if condition[0] == '>': write(f'JLT {condition[1]} {condition[2]} {LABEL}')
            elif condition[0] == '<': write(f'JLT {condition[2]} {condition[1]} {LABEL}')

            temp_stack.append(f'LAB {LABEL}')
        
        elif current_line == 'endif':
            write(temp_stack.pop())

        counter += 1

def err(code: int, msg: str, error='') -> None:
    global current_line, file

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
          \n  File {file}, line {counter}\
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

    input = sys.argv[1]
    output = sys.argv[2]
    if not os.path.isfile(input): err(0, 'Input file not exists.')
    with open(output, 'w') as f: f.write('')

    file = input
    main(input)