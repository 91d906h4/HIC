# Import required modules
import re
import os
import sys
import time
import random

# Global parameters
linePointer = 0 # The line executer currently running on.
generatorStack = [] # Used to save generated code.
labelStack = [[]] # Used to store labels of if-else condition, for-loop, and while-loop.
operatorWeight = { # Definde the weight of operators. Operator with small number has a higher weight.
    ",": 0,
    "(": 0,
    "[": 0,
    "**": 1,
    "++": 1,
    "*": 2,
    "/": 2,
    "%": 2,
    "+": 3,
    "-": 3,
    "<<": 4,
    ">>": 4,
    "<": 5,
    ">": 5,
    "<=": 5,
    ">=": 5,
    "==": 6,
    "!=": 6,
    "&": 7,
    "^": 7,
    "|": 7,
    "not": 8,
    "and": 9,
    "or": 10,
    "]": 11,
    ")": 11
}

# Virtual Label Generator
def virtualLabelGenerator(length: int = 16) -> str:
    return ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(length)])

# String spliter
def stringSpliter(string: str, pattern: str = ' ', limit: int = 0, ignore: list = []) -> list:
    r"""
    Split the string with pattern.
    
    Parameters
    ---
    string : str
        Input string.

    pattern: str
        Char or string to split a string.
        For exmaple, pattern=' ' means, using space to split a string.

    ignore: list
        The char or string in ignore list will be ignore if this char or string is not in a string (starts with '"' and ends with '"').

    Returns
    ---
    list
        Splited string list.
    """
    assert pattern not in ignore # Pattern and ignore cannot be the same string.

    result, temp, inString = [], "", False

    for i in string:
        if i == '"': inString = not inString

        if i in ignore and not inString: continue
        elif i == pattern and not inString:
            if temp != "": result.append(temp)
            temp = ""
            limit -= 1
            if limit == 0: break
        else: temp += i

    if temp != "": result.append(temp)

    return result

def typeOf(string: str) -> str:
    r"""
        Return the type of input string.
        (1) operator
        (2) integer
        (3) float
        (4) string
        (5) bool
        (6) parameter
        (7) systme code (System code starts with '!')
    """

    if string in list(operatorWeight.keys()):
        return "operator"
    elif str(string).count('"') == 2 and str(string)[0] == '"' and str(string)[-1] == '"':
        return "string"
    elif string in ["true", "false", "null"]:
        return "bool"
    elif string[0] == '!':
        return "system code"

    try:
        float(string)
        return "float"
    except: pass
    
    try:
        int(string)
        return "integer"
    except: pass

    return "parameter"

###################################################################################################

def expressionParser(expression: str) -> list:
    r"""
    Split string into operators, variables and expressions.
    Use expressionGenerator(expressionSolver(expressionParser("INPUT_STRING"))) to get a generation code list.

    For example:
        raw_text = '(3 + a ** 8) / 7 + 5 / (5 % 9)'
        code_list = expressionGenerator(expressionSolver(expressionParser(raw_text)))

    Generated code list 'code_list':
        ['LDA 3', 'LDA $a', 'LDA 8', 'EXP _ _', 'ADD _ _', 'LDA 7', 'DIV _ _', 'LDA 5', 'LDA 5', 'LDA 9', 'REM _ _', 'DIV _ _', 'ADD _ _']
    """
    parseStack, expression, inString = [], '(' + expression + ' )', False

    i, temp = 0, ""
    while i < len(expression):
        if expression[i] == ' ' and not inString:
            if temp != '': parseStack.append(temp)
            temp = ""
            i += 1
        elif expression[i] == '"':
            inString = not inString
            temp += expression[i]
            i += 1
        elif typeOf(expression[i:i+3]) == "operator" and not inString:
            if temp != '': parseStack.append(temp)
            temp = ""
            parseStack.append(expression[i:i+3])
            i += 3
        elif typeOf(expression[i:i+2]) == "operator" and not inString:
            if temp != '': parseStack.append(temp)
            temp = ""
            parseStack.append(expression[i:i+2])
            i += 2
        elif typeOf(expression[i]) == "operator" and not inString:
            if temp != '': parseStack.append(temp)
            temp = ""
            parseStack.append(expression[i])
            i += 1
        else:
            temp += expression[i]
            i += 1

    # Negative number
    i = len(parseStack) - 1
    while i >= 0:
        if parseStack[i] == '-' and i > 0 and typeOf(parseStack[i - 1]) == "operator" and typeOf(parseStack[i + 1]) in ["integer", "float"]:
            parseStack[i + 1] = '-' + parseStack[i + 1]
            del parseStack[i]
        i -= 1

    resultStack = [[]]
    for i in parseStack:
        if i in '([': resultStack.append([i])
        elif i in ')]':
            resultStack[-1].append(i)
            resultStack[-2].append(resultStack[-1])
            resultStack.pop()
        else: resultStack[-1].append(i)

    return resultStack

def expressionSolver(expression: list) -> None:
    global generatorStack, operatorWeight
    operatorStack = []

    i = 0
    while i < len(expression):
        temp = expression[i]
        if isinstance(temp, list):
            isArry = bool(temp[0] == '[' and temp[-1] == ']') # Check if an array.
            isFunction = bool(i > 0 and typeOf(expression[i - 1]) == "parameter" and temp[0] == '(') # Check if a function.

            parameter = ""
            if isFunction:
                parameter = generatorStack.pop()
                generatorStack.append("!FUNC_STR")
            if isArry:
                parameter = generatorStack.pop()
                generatorStack.append("!ARRAY_STR")
            expressionSolver(temp) # Solve recursively
            if isArry:
                generatorStack.append(parameter)
                generatorStack.append('!ARRAY_END')
            if isFunction:
                generatorStack.append(parameter)
                generatorStack.append("!FUNC_END")

        if typeOf(temp) == "operator":
            if temp == ',': generatorStack.append(temp)
            elif operatorStack == []: operatorStack.append(temp)
            elif operatorWeight[operatorStack[-1]] <= operatorWeight[temp]:
                operatorPop = operatorStack.pop()
                if operatorPop not in '([':
                    generatorStack.append(operatorPop)
                if temp in ')]' and operatorStack != []:
                    generatorStack.append(operatorStack.pop())
                else: i -= 1
            else: operatorStack.append(temp)
        elif not isinstance(temp, list): generatorStack.append(temp)

        i += 1

    return generatorStack

def expressionGenerator(expression: str, n: int = 0) -> None:
    global generatorStack
    inSystemCode, counterStack, result, generatorStack = 0, [1], [], []

    for i in range(len(expression)):
        exp = expression[i]
        t = typeOf(exp)
        if t in ["integer", "float", "string", "bool"]: result.append("LDA " + exp)
        elif t == "operator":
            # Arithmetic
            if exp == '+': result.append("ADD _ _")
            elif exp == '++':
                result.append("LDA 1")
                result.append("ADD _ _")
            elif exp == '-': result.append("SUB _ _")
            elif exp == '*': result.append("MUL _ _")
            elif exp == '/': result.append("DIV _ _")
            elif exp == '**': result.append("EXP _ _") # Exponentiation
            elif exp == '%': result.append("REM _ _") # Remainder

            # Compare
            elif exp == '==': result.append("EQL _ _") # Equal
            elif exp == '!=': result.append("NEQ _ _") # Not Equal
            elif exp == '>': result.append("GRT _ _") # Greater Than
            elif exp == '<': result.append("LST _ _") # Less Than
            elif exp == '>=': result.append("GTE _ _") # Greater Than or Equal
            elif exp == '<=': result.append("LTE _ _") # Less Than or Equal

            # Bit Operators
            elif exp == '>>': result.append("BSL _ _") # Bit Shift Left
            elif exp == '<<': result.append("BSR _ _") # Bit Shift Right
            elif exp == '&': result.append("BAD _ _") # Bit AND
            elif exp == '^': result.append("BXR _ _") # Bit XOR
            elif exp == '|': result.append("BOR _ _") # Bit OR

            # Logical Operators
            elif exp == 'and': result.append("LAD _ _") # Logical AND
            elif exp == 'or': result.append("LOR _ _") # Logical OR
            elif exp == 'not': result.append("LNT _") # Logical NOT

            # Else
            elif exp == ',': counterStack[-1] += 1
            else: result.append(exp) # Undeclared
        elif t == "parameter":
            if i + 1 < len(expression) and expression[i + 1] == "!FUNC_END": result.append("CALL " + exp)
            elif i + 1 < len(expression) and expression[i + 1] == "!ARRAY_END": result.append("LDAA $" + exp + " _" * counterStack.pop())
            else: result.append("LDA $" + exp)
        elif t == "system code":
            if exp in ["!FUNC_STR", "!ARRAY_STR"]:
                counterStack.append(1)
                inSystemCode += 1
            elif exp in ["!FUNC_END", "!ARRAY_END"]: inSystemCode -= 1
        else: result.append(exp)

    return result

class Generator:
    def __init__(self, lines: str, output: str) -> None:
        self.lines = lines
        outputFile = open(output, 'w')
        outputFile.write('')
        self.outputFile = open(output, 'a')

        global generatorStack
    
    def __call__(self) -> None:

        linePointer = 0
        while linePointer < len(self.lines):
            line: str = self.lines[linePointer]

            ####################################################################################################
            # Declaration

            if re.match(r"^(int|float|string|bool) +[a-zA-Z_][a-zA-Z0-9_]* *(= *.*)?$", line):
                self.DECLARATION(line)

            elif re.match(r"^(int|float|bool|string) +[a-zA-Z_][a-zA-Z0-9_]*\[.*\] *(= *\[.*\])?$", line):
                self.DECLARATION_ARR(line)

            ####################################################################################################
            # Return

            elif re.match(r"return +.*", line): self.RETURN(line)

            ####################################################################################################
            # If-else condition

            elif re.match(r"if *\(.*\) *", line): self.IF(line)
            
            elif re.match(r"(else if|elif)", line): self.ELIF(line)
            
            elif re.match(r"else", line): self.ELSE(line)

            elif re.match(r"}", line):
                if linePointer + 1 < len(self.lines) and (self.lines[linePointer + 1].startswith('else if') or self.lines[linePointer + 1].startswith('elif') or self.lines[linePointer + 1].startswith('else')): pass
                elif labelStack[-1][0] == "IF":
                    for i in labelStack[-1][1:]:
                        self.outputFile.write("LABEL " + i + "\n")
                    labelStack.pop()
                elif labelStack[-1][0] in ["WHILE", "FUNCTION"]:
                    for i in labelStack[-1][1:]:
                        self.outputFile.write(i + "\n")
                    labelStack.pop()
                elif labelStack[-1][0] == "FOR":
                    self.ASSIGNMENT(labelStack[-1][1])
                    for i in labelStack[-1][2:]:
                        self.outputFile.write(i + "\n")
                    labelStack.pop()
            
            ####################################################################################################
            # Loop

            elif re.match(r"for *\(.*;.*;.*\)", line):
                label, endLabel = virtualLabelGenerator(), virtualLabelGenerator()
                line = line[line.find('(') + 1:line.rfind(')')]
                line = stringSpliter(line, pattern=';')

                # Generate code
                self.DECLARATION(line[0])

                self.outputFile.write("LABEL " + label + "\n")

                for i in expressionGenerator(expressionSolver(expressionParser(line[1]))): self.outputFile.write(i + '\n')

                self.outputFile.write("LNT _ \n")
                self.outputFile.write("JMP _ " + endLabel + "\n")

                labelStack.append(["FOR", line[2], "JMP 1 " + label, "LABEL " + endLabel])

            elif re.match(r"while *\(.*\)", line):
                label, endLabel = virtualLabelGenerator(), virtualLabelGenerator()
                line = line[line.find('(') + 1:line.rfind(')')]

                self.outputFile.write("LABEL " + label + "\n")

                for i in expressionGenerator(expressionSolver(expressionParser(line))): self.outputFile.write(i + '\n')

                self.outputFile.write("LNT _ \n")
                self.outputFile.write("JMP _ " + endLabel + "\n")

                labelStack.append(["WHILE", "JMP 1 " + label, "LABEL " + endLabel])

            ####################################################################################################
            # Function

            elif re.match(r"function +[a-zA-Z_][a-zA-Z0-9_]*\(.*\)", line):
                self.outputFile.write("SSKP\n")
                function, variable = line.split('(', 1)
                function = function[9:].strip()
                variable = stringSpliter(variable[:-1], pattern=',')

                self.outputFile.write(":" + function + "\n")

                for i in variable: self.DECLARATION(i.strip(), "_")

                labelStack.append(["FUNCTION", "ESKP"])

            ####################################################################################################
            # Output

            elif re.match(r"print *\(.*\)", line):
                line = line[line.find('(') + 1:line.rfind(')')]
                line = stringSpliter(line, pattern=',')

                for i in reversed(line):
                    for i in expressionGenerator(expressionSolver(expressionParser(i))): self.outputFile.write(i + '\n')
                
                self.outputFile.write("MSG" + " _" * len(line) + "\n")

            ####################################################################################################
            # System Tools

            # Flag
            elif re.match(r"===>.*<===", line):
                self.outputFile.write("; " + line + "\n")

            ####################################################################################################
            # Assignment

            elif re.match(r".*(\+|\-|\*|\/)?=.*", line):
                self.ASSIGNMENT(line)

            ####################################################################################################

            # Update line pointer
            linePointer += 1

    ####################################################################################################

    def ASSIGNMENT(self, line: str) -> None:
        line = stringSpliter(line, pattern='=')
        if '[' in line[0] and ']' in line[0]:
            variable, dim = line[0][:line[0].find('[')].strip(), stringSpliter(line[0][line[0].find('['):].replace('][', ',').strip()[1:-1], pattern=',')
            value = re.sub(r'\[|\]', '', line[1])

            # Generate code
            for i in reversed(stringSpliter(value, pattern=',')):
                for i in expressionGenerator(expressionSolver(expressionParser(i))): self.outputFile.write(i + '\n')
            for i in dim:
                for i in expressionGenerator(expressionSolver(expressionParser(i))): self.outputFile.write(i + '\n')
            self.outputFile.write("STAA $" + variable + " _" * len(dim) + "\n")
        else:
            # Generate code
            for i in expressionGenerator(expressionSolver(expressionParser(line[1]))): self.outputFile.write(i + '\n')
            self.outputFile.write("STA $" + line[0].strip() + "\n")

    def DECLARATION(self, line: str, default: str = "") -> None:
        # Get the type of variable.
        replacement, variableType, initial = 0, "", ""
        if line.startswith('int'): replacement, variableType, initial = 3, "INT" ,"0"
        elif line.startswith('bool'): replacement, variableType, initial = 4, "BOOL" ,"false"
        elif line.startswith('float'): replacement, variableType, initial = 5, "FLOAT" ,"0.0"
        elif line.startswith('string'): replacement, variableType, initial = 6, "STR" ,"\"\""

        line = line[replacement:] # Remove int declaration-spasifier
        if line.find('=') == -1: self.outputFile.write(variableType + " $" + line.replace(' ', '') + " " + (default if default != "" else initial) + "\n")
        else:
            variable, value = line.split('=', 1)
            variable = variable.replace(' ', '')
            self.outputFile.write(variableType + " $" + variable + " " + (default if default != "" else initial) + "\n")

            # Generate code
            for i in expressionGenerator(expressionSolver(expressionParser(value))): self.outputFile.write(i + '\n')
            self.outputFile.write("STA $" + variable + "\n")

    def DECLARATION_ARR(self, line: str) -> None:
        # Get the type of variable.
        replacement, variableType = 0, ""
        if line.startswith('int'): replacement, variableType = 3, "INTA"
        elif line.startswith('bool'): replacement, variableType = 4, "BOOLA"
        elif line.startswith('float'): replacement, variableType = 5, "FLOATA"
        elif line.startswith('string'): replacement, variableType = 6, "STRA"

        line = line[replacement:] # Remove int declaration-spasifier
        if line.find('=') == -1:
            variable, dim = line[:line.find('[')].strip(), stringSpliter(line[line.find('['):].replace('][', ' ')[1:-1], ignore=[','])
            for i in dim:
                for i in expressionGenerator(expressionSolver(expressionParser(i))): self.outputFile.write(i + '\n')

            self.outputFile.write(variableType + " $" + variable + " _" * len(dim) + "\n")
        else:
            line = stringSpliter(line, pattern='=')
            variable, dim = line[0][:line[0].find('[')].strip(), stringSpliter(line[0][line[0].find('['):].replace('][', ',').strip()[1:-1], pattern=',')
            value = re.sub(r'\[|\]', '', line[1])

            # Generate code
            for i in dim:
                for i in expressionGenerator(expressionSolver(expressionParser(i))): self.outputFile.write(i + '\n')
            self.outputFile.write(variableType + " $" + variable + " _" * len(dim) + "\n")
            for i in reversed(stringSpliter(value, pattern=',')):
                for i in expressionGenerator(expressionSolver(expressionParser(i))): self.outputFile.write(i + '\n')
            for i in range(len(stringSpliter(value, pattern=','))): self.outputFile.write("STAA $" + variable + " " + str(i) + "\n")

    def RETURN(self, line: str) -> None:
        line = line.replace("return", "", 1)

        # Generate code
        for i in expressionGenerator(expressionSolver(expressionParser(line))): self.outputFile.write(i + '\n')
        self.outputFile.write("RET\n")
    
    def IF(self, line: str) -> None:
        line = line[line.find('(') + 1:line.rfind(')')]
        label, endLabel = virtualLabelGenerator(), virtualLabelGenerator()

        for i in expressionGenerator(expressionSolver(expressionParser(line))): self.outputFile.write(i + '\n')

        self.outputFile.write("LNT _ \n")
        self.outputFile.write("JMP _ " + label + "\n")

        labelStack.append(["IF", endLabel, label])
    
    def ELIF(self, line: str) -> None:
        line = line[line.find('(') + 1:line.rfind(')')]
        label = virtualLabelGenerator()

        # End label
        if len(labelStack[-1]) > 1: self.outputFile.write("JMP 1 " + labelStack[-1][1] + "\n")
        self.outputFile.write("LABEL " + labelStack[-1].pop() + "\n")

        for i in expressionGenerator(expressionSolver(expressionParser(line))): self.outputFile.write(i + '\n')

        self.outputFile.write("LNT _ \n")
        self.outputFile.write("JMP _ " + label + "\n")

        labelStack[-1].append(label)
    
    def ELSE(self, line: str) -> None:
        if len(labelStack[-1]) > 1:
            self.outputFile.write("JMP 1 " + labelStack[-1][1] + "\n")
        self.outputFile.write("LABEL " + labelStack[-1].pop() + "\n")

def preposeccor(file: str) -> list:
    inArray, inString, inFunction, inComment, inSingleComment = 0, False, False, 0, False # If pointer is in a array, string, function, or a comment.
    temp, lines, i, l = "", [], 0, len(file)

    while i < l:
        char = file[i]
        if char == '"': inString = not inString
        elif not inString and i  + 1 < l and char + file[i + 1] == '/*': inComment += 1
        elif not inString and i  + 1 < l and char + file[i + 1] == '*/':
            inComment -= 1
            i += 2
            continue
        elif not inString and i  + 1 < l and char + file[i + 1] == '//': inSingleComment = True
        elif char == '\n': inSingleComment = False

        if inComment > 0 or inSingleComment:
            # Remove multi-lines comment
            i += 1
            continue
        elif char == '\n':
            if inArray == 0:
                if temp != '': lines.append(temp)
                temp = ""
        elif char == ';':
            if inFunction > 0 or inString: temp += char
            else:
                lines.append(temp)
                temp = ""
        elif char in ['{', '}']:
            if not inString:
                if temp != '': lines.append(temp)
                temp = ""
                lines.append(char)
        else:
            if not inString and not inComment:
                if char == '[': inArray += 1
                elif char == ']': inArray -= 1
                elif char == '(': inFunction += 1
                elif char == ')': inFunction -= 1
                
            temp += char
        
        i += 1

    lines.append(temp)

    # Remove empty line
    lines = [x.strip() for x in lines if x.strip() != '']

    return lines

def main(file: str, outputFile: str) -> None:

    lines = preposeccor(file)

    # Import modules
    for line in lines:
        line: str

        if re.match(r"#import", line):
            importFile = line[7:].strip()[1:-1]
            importFile = "./hmodule/" + importFile
            
            if not os.path.isfile(importFile): error(0, f"Import modules {importFile} not found.")

            modeule = open(importFile, "r").read()
            lines.extend(preposeccor(modeule))

    Generator(lines, outputFile)()

# Error handler
def error(code: int, message: str) -> None:
    r"""
        Error Codes:
            0: "Input Error",
            1: "Undefined",
            2: "Syntax Error",
            3: "Type Error",
            4: "Value Error",
            5: "Defined"
    """
    global linePointer

    codes = {
        0: "Input Error",
        1: "Undefined",
        2: "Syntax Error",
        3: "Type Error",
        4: "Value Error",
        5: "Defined"
    }

    print(f'Traceback:\
          \n  File {file}, line {linePointer}\
          \n    {""}\
          \n      ^^^\
          \n{codes[code]}: {message}'
    )
    exit()

if __name__ == "__main__":
    START_COMPILE = time.time()

    # If there is no input assembly file, throw error.
    if len(sys.argv) < 2: error(0, "Input file has not been specified.")
    
    filename = sys.argv[1]
    if not os.path.isfile(filename): error(0, f"Input file {filename} not exists.")

    file = open(filename, "r").read()
    main(file, sys.argv[2])

    FINISH_COMPILE = time.time()

    print(f'Compiled successfuly.\
          \nTotal complie time: {FINISH_COMPILE - START_COMPILE}'
    )