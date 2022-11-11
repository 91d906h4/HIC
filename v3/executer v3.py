import os
import sys

# Params
params = {}
counter = 0
current_line = ''
file = ''

class Checker:
    def __init__(self, input_text: str) -> None:
        self.input_text = input_text
    
    def isValidParam(self, exit=True):
        if self.input_text[0] == '$' and len(self.input_text) > 1 and not self._isInt(self.input_text[1:]): return True
        else:
            if exit: err(3, f'{self.input_text} is not a valid params.', self.input_text)
            else: return False
    
    def isValidValue(self, exit=True):
        if self._isInt(self.input_text) or self._isStr(self.input_text) or self._isFloat(self.input_text)or self._isParam(self.input_text): return True
        else:
            if exit: err(3, f'{self.input_text} is not a valid value.', self.input_text)
            else: return False

    def isExistsParam(self, exit=True):
        if self.input_text[0] == '$' and self.input_text[1:] in params: return True
        else:
            if exit: err(1, f'Param {self.input_text} has not been defined.')
            else: return False

    def isExistsLabel(self, exit=True):
        if "L_" + str(self.input_text) in params: return True
        else:
            if exit: err(1, f'Label {self.input_text} has not been defined.', self.input_text)
            else: return False

    def getType(self, exit=True, pure=False):
        if self._isInt(self.input_text): return 'int'
        if self._isStr(self.input_text): return 'str'
        if self._isFloat(self.input_text): return 'float'
        if self._isArr(self.input_text): return 'arr'
        if self._isParam(self.input_text): return ('' if pure else 'p_') + params[self.input_text[1:]]['type']
        else:
            if exit: err(3, f'{self.input_text} has invald type.')
            else: return False

    def _isInt(self, input_text, exit=False):
        try:
            int(input_text)
        except:
            if exit: err(3, f'{input_text} is not an integer.')
            else: return False
        return True

    def _isFloat(self, input_text, exit=False):
        try:
            float(input_text)
        except:
            if exit: err(3, f'{input_text} is not a float.')
            else: return False
        return True
    
    def _isStr(self, input_text: str, exit=False):
        if input_text.count('\'') == 2 and input_text[0] == '\'' and input_text[-1] == '\'': return True
        else:
            if exit: err(3, f'{input_text} is not a string.')
            else: return False
    
    def _isArr(self, input_text: str, exit=False):
        if type(input_text) is list: return True
        else:
            if exit: err(3, f'{input_text} is not a array.')
            else: return False

    def _isParam(self, input_text, exit=False):
        if input_text[0] == '$' and self.isExistsParam(self.input_text): return True
        else:
            if exit: err(3, f'{self.input_text} is not a param.')
            else: return False

    def _isLabel(self, input_text, exit=False):
        if input_text[0] == '$' and self.isExistsLabel(self.input_text): return True
        else:
            if exit: err(3, f'{self.input_text} is not a label.')
            else: return False

class Operation:
    def __init__(self, content: str) -> None:
        temp_content = []
        temp = ''
        str_locker = False
        for i in content:
            if i == ' ' and str_locker == False:
                temp_content.append(temp)
                temp = ''
            elif i == '\'' and str_locker == False:
                temp += i
                str_locker = True
            elif i == '\'' and str_locker == True:
                temp_content.append(temp + "'")
                temp = ''
                str_locker = False
            else: temp += i

        temp_content.append(temp)
        self.content = temp_content
        while '' in self.content: self.content.remove('')

    def val(self):
        if(len(self.content) != 2): err(2, f'Except 2 params, {len(self.content)} given.')

        par1, par2 = self.content

        chk1 = Checker(par1)
        chk2 = Checker(par2)

        chk1.isValidParam()
        chk2.isValidValue()

        val = ''
        chk2_type = chk2.getType()
        match chk2_type:
            case 'str': val = par2[1:-1]
            case 'int': val = int(par2)
            case 'float': val = float(par2)
            case 'arr': val = par2
            case 'p_str': val = str(params[par2[1:]]['val'])
            case 'p_int': val = int(params[par2[1:]]['val'])
            case 'p_float': val = float(params[par2[1:]]['val'])
            case 'p_arr': val = params[par2[1:]]['val']

        params[par1[1:]] = {
            'type': chk2_type.replace('p_', ''),
            'val': val
        }

    def arr(self):
        if(len(self.content) < 2): err(2, f'Except at least 2 params, {len(self.content)} given.')

        par1 = self.content[0]
        par2 = ''.join(self.content[1:]).split(',')
        while '' in par2: par2.remove('')

        chk1 = Checker(par1)
        chk2 = Checker(par2)
        
        chk1.isValidParam()
        chk2._isArr(par2, exit=True)

        for i, content in enumerate(par2):
            chk_content = Checker(content).getType()
            if chk_content == 'int': par2[i] = int(content)
            elif chk_content == 'float': par2[i] = float(content)
            elif chk_content == 'str': par2[i] = content[1:-1]
            elif chk_content == 'p_int': par2[i] = int(params[content[1:]]['val'])
            elif chk_content == 'p_float': par2[i] = float(params[content[1:]]['val'])
            elif chk_content == 'p_str': par2[i] = str(params[content[1:]]['val'])

        params[par1[1:]] = {
            'type': 'arr',
            'val': par2
        }

    def lab(self):
        if(len(self.content) != 1): err(2, f'Except 1 params, {len(self.content)} given.')

        par1 = self.content[0]

        chk1 = Checker(par1)

        if chk1.getType(exit=False) != False: err(3, f'{par1} is not valid label.', par1)
        else: params["L_" + str(par1)] = counter

    def add(self):
        if(len(self.content) != 2): err(2, f'Except 2 params, {len(self.content)} given.')

        par1, par2 = self.content
        chk1 = Checker(par1)
        chk2 = Checker(par2)

        chk1.isExistsParam()
        chk1_type = chk1.getType(pure=True)
        chk2_type = chk2.getType()

        if chk2_type.startswith('p_'):
            chk2_type = chk2_type[2:]
            par2 = params[par2[1:]]['val']

        if chk1_type == chk2_type:
            if chk1_type == 'str':
                params[par1[1:]]['val'] += par2
            elif chk1_type == 'int':
                params[par1[1:]]['val'] += int(par2)
            elif chk1_type == 'float':
                params[par1[1:]]['val'] += float(par2)
        else: err(5, f'Type of {par1} ({chk1_type}) did not match {par2} ({chk2_type}).', par1)

    def sub(self):
        if(len(self.content) != 2): err(2, f'Except 2 params, {len(self.content)} given.')

        par1, par2 = self.content
        chk1 = Checker(par1)
        chk2 = Checker(par2)

        chk1.isExistsParam()
        chk1_type = chk1.getType(pure=True)
        chk2_type = chk2.getType()

        if chk2_type.startswith('p_'):
            chk2_type = chk2_type[2:]
            par2 = params[par2[1:]]['val']

        if chk1_type == chk2_type:
            if chk1_type == 'int':
                params[par1[1:]]['val'] -= int(par2)
            elif chk1_type == 'float':
                params[par1[1:]]['val'] -= float(par2)
        else: err(5, f'Type of {par1} ({chk1_type}) did not match {par2} ({chk2_type}).', par1)

    def mul(self):
        if(len(self.content) != 2): err(2, f'Except 2 params, {len(self.content)} given.')

        par1, par2 = self.content
        chk1 = Checker(par1)
        chk2 = Checker(par2)

        chk1.isExistsParam()
        chk1_type = chk1.getType(pure=True)
        chk2_type = chk2.getType()

        if chk2_type.startswith('p_'):
            chk2_type = chk2_type[2:]
            par2 = params[par2[1:]]['val']

        if chk1_type == chk2_type:
            if chk1_type == 'int':
                params[par1[1:]]['val'] *= int(par2)
            elif chk1_type == 'float':
                params[par1[1:]]['val'] *= float(par2)
        else: err(5, f'Type of {par1} ({chk1_type}) did not match {par2} ({chk2_type}).', par1)

    def div(self):
        if(len(self.content) != 2): err(2, f'Except 2 params, {len(self.content)} given.')

        par1, par2 = self.content
        chk1 = Checker(par1)
        chk2 = Checker(par2)

        chk1.isExistsParam()
        chk1_type = chk1.getType(pure=True)
        chk2_type = chk2.getType()

        if chk2_type.startswith('p_'):
            chk2_type = chk2_type[2:]
            par2 = params[par2[1:]]['val']

        if chk1_type == chk2_type:
            if chk1_type == 'int':
                params[par1[1:]]['val'] /= int(par2)
            elif chk1_type == 'float':
                params[par1[1:]]['val'] /= float(par2)
        else: err(5, f'Type of {par1} ({chk1_type}) did not match {par2} ({chk2_type}).', par1)

    def jeq(self):
        global counter
        if(len(self.content) != 3): err(2, f'Except 3 params, {len(self.content)} given.')

        par1, par2, par3 = self.content
        chk1 = Checker(par1)
        chk2 = Checker(par2)
        chk3 = Checker(par3)

        chk3.isExistsLabel()
        chk1_type = chk1.getType()
        chk2_type = chk2.getType()

        if chk1_type.startswith('p_'):
            chk1_type = chk1_type[2:]
            par1 = params[par1[1:]]['val']
        if chk2_type.startswith('p_'):
            chk2_type = chk2_type[2:]
            par2 = params[par2[1:]]['val']

        if chk1_type == chk2_type:
            if chk1_type == 'int':
                if int(par1) == int(par2): counter = params["L_" + str(par3)]
            elif chk1_type == 'float':
                if float(par1) == float(par2): counter = params["L_" + str(par3)]
            elif chk1_type == 'str':
                par1 = str(par1).replace("'", '')
                par2 = str(par2).replace("'", '')
                if str(par1) == str(par2): counter = params["L_" + str(par3)]
        else: err(5, f'Type of {par1} ({chk1_type}) did not match {par2} ({chk2_type}).', par1)

    def jnq(self):
        global counter
        if(len(self.content) != 3): err(2, f'Except 3 params, {len(self.content)} given.')

        par1, par2, par3 = self.content
        chk1 = Checker(par1)
        chk2 = Checker(par2)
        chk3 = Checker(par3)

        chk3.isExistsLabel()
        chk1_type = chk1.getType()
        chk2_type = chk2.getType()

        if chk1_type.startswith('p_'):
            chk1_type = chk1_type[2:]
            par1 = params[par1[1:]]['val']
        if chk2_type.startswith('p_'):
            chk2_type = chk2_type[2:]
            par2 = params[par2[1:]]['val']

        if chk1_type == chk2_type:
            if chk1_type == 'int':
                if int(par1) != int(par2): counter = params["L_" + str(par3)]
            elif chk1_type == 'float':
                if float(par1) != float(par2): counter = params["L_" + str(par3)]
            elif chk1_type == 'str':
                par1 = str(par1).replace("'", '')
                par2 = str(par2).replace("'", '')
                if str(par1) != str(par2): counter = params["L_" + str(par3)]
        else: err(5, f'Type of {par1} ({chk1_type}) did not match {par2} ({chk2_type}).', par1)

    def jlt(self):
        global counter
        if(len(self.content) != 3): err(2, f'Except 3 params, {len(self.content)} given.')

        par1, par2, par3 = self.content
        chk1 = Checker(par1)
        chk2 = Checker(par2)
        chk3 = Checker(par3)

        chk3.isExistsLabel()
        chk1_type = chk1.getType()
        chk2_type = chk2.getType()

        if chk1_type.startswith('p_'):
            chk1_type = chk1_type[2:]
            par1 = params[par1[1:]]['val']
        if chk2_type.startswith('p_'):
            chk2_type = chk2_type[2:]
            par2 = params[par2[1:]]['val']

        if chk1_type == chk2_type:
            if chk1_type == 'int':
                if int(par1) < int(par2): counter = params["L_" + str(par3)]
            elif chk1_type == 'float':
                if float(par1) < float(par2): counter = params["L_" + str(par3)]
            elif chk1_type == 'str':
                if str(par1) < str(par2): counter = params["L_" + str(par3)]
        else: err(5, f'Type of {par1} ({chk1_type}) did not match {par2} ({chk2_type}).', par1)

    def jle(self):
        global counter
        if(len(self.content) != 3): err(2, f'Except 3 params, {len(self.content)} given.')

        par1, par2, par3 = self.content
        chk1 = Checker(par1)
        chk2 = Checker(par2)
        chk3 = Checker(par3)

        chk3.isExistsLabel()
        chk1_type = chk1.getType()
        chk2_type = chk2.getType()

        if chk1_type.startswith('p_'):
            chk1_type = chk1_type[2:]
            par1 = params[par1[1:]]['val']
        if chk2_type.startswith('p_'):
            chk2_type = chk2_type[2:]
            par2 = params[par2[1:]]['val']

        if chk1_type == chk2_type:
            if chk1_type == 'int':
                if int(par1) <= int(par2): counter = params["L_" + str(par3)]
            elif chk1_type == 'float':
                if float(par1) <= float(par2): counter = params["L_" + str(par3)]
            elif chk1_type == 'str':
                if str(par1) <= str(par2): counter = params["L_" + str(par3)]
        else: err(5, f'Type of {par1} ({chk1_type}) did not match {par2} ({chk2_type}).', par1)
    
    def msg(self):
        par1 = self.content[0]
        chk1 = Checker(par1)

        chk1_type = chk1.getType()

        if chk1.isExistsParam(exit=False): print(params[par1[1:]]['val'])
        elif chk1_type == 'str': print(par1[1:-1])
        elif chk1_type in ['int', 'float']: print(par1)
        else: err(3, f'{par1} is not a valid value.')
    
    def ipt(self):
        par1 = self.content[0]
        chk1 = Checker(par1)

        chk1.isValidParam(exit=True)
        par2 = input()
        chk2 = Checker(par2)

        chk1.isValidParam()
        chk2.isValidValue()

        val = ''
        chk2_type = chk2.getType()
        match chk2_type:
            case 'str': val = par2[1:-1]
            case 'int': val = int(par2)
            case 'float': val = float(par2)
            case 'arr': val = par2
            case 'p_str': val = str(params[par2[1:]]['val'])
            case 'p_int': val = int(params[par2[1:]]['val'])
            case 'p_float': val = float(params[par2[1:]]['val'])
            case 'p_arr': val = params[par2[1:]]['val']

        params[par1[1:]] = {
            'type': chk2_type.replace('p_', ''),
            'val': val
        }

def err(code: int, msg: str, error='') -> None:
    global current_line, file

    codes = {
        0: "input_text Error",
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

def main(input_text: str) -> None:
    global counter, current_line
    lines = {}

    # Preprocessing
    for x, y in enumerate(open(input_text)):
        y = y.replace('\n', '')
        comments = y.find('#')
        if comments != -1: y = y[:comments]
        lines[x] = y

    # Pass 1
    while counter < len(lines):
        current_line = lines[counter]

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
            case 'LAB': opIns.lab()
            case 'ARR': opIns.arr()
        
        counter += 1

    counter = 0

    # Pass 2
    while counter < len(lines):
        current_line = lines[counter]

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
            case 'ARR': opIns.arr()
            case 'ADD': opIns.add()
            case 'SUB': opIns.sub()
            case 'MUL': opIns.mul()
            case 'DIV': opIns.div()
            case 'JEQ': opIns.jeq()
            case 'JNQ': opIns.jnq()
            case 'JLT': opIns.jlt()
            case 'JLE': opIns.jle()
            case 'LAB': opIns.lab()
            case 'MSG': opIns.msg()
            case 'IPT': opIns.ipt()
            case 'END': exit()
        
        counter += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('input_text Error: input_text file not specified.')
        exit()

    input_text = sys.argv[1]
    if not os.path.isfile(input_text): err(0, 'input_text file not exists.')

    file = input_text
    main(input_text)