# Import required modules
import re
import os
import sys
import random

# Global parameters
variableStack = [{}] # Variable name -> VariableType
memory = {} # Address -> Value
jumper = {} # Label name -> Line Point
returnStack = [] # Store return opinter
register = [] # Register is a stack, store variable or temporary address
linePointer = 0 # The line executer currently running on

# Address Generator
def addressGenerator() -> str:
    return hex(random.randint(0, 4294967295))

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
        Return the type of input string.=
        (1) integer
        (2) float
        (3) string
        (4) bool
        (5) parameter
        (6) systme code (System code starts with '!')
    """

    if str(string).count('"') == 2 and str(string)[0] == '"' and str(string)[-1] == '"':
        return "string"
    elif string in ["true", "false", "null"]:
        return "bool"
    
    try:
        if str(int(string)) == str(string):
            int(string)
            return "integer"
    except: pass

    try:
        assert "." in str(string)
        float(string)
        return "float"
    except: pass

    return "parameter"

def autoConvert(string: str):
    typeOfString = typeOf(string)

    if typeOfString == "string": return str(string[1:-1])
    elif typeOfString == "integer": return int(string)
    elif typeOfString == "float": return float(string)
    elif typeOfString == "bool":
        if string == "true": return True
        elif string == "false": return False
        else: return None
    else: return string

# Variable type
class VariableType:
    def __init__(self, type: str, address: str, shape: str = []) -> None:
        self.type = type
        self.shape = shape
        self.address = address

def main(file: str) -> None:
    global linePointer
    inSkipArea = 0

    lines = file.split('\n')

    # Pre-processing
    # Remove comments and empty lines.
    for i, line in enumerate(lines):
        inString, temp = False, ""
        for j in line:
            if j == '"': inString = not inString
            if j == ';' and not inString:
                lines[i] = temp
                break
            else: temp += j

    # lines = [x for x in lines if x != '']

    # First Pass
    # To locate labels and functions.
    for i, line in enumerate(lines):
        if line.startswith(':'): # Function
            jumper[line[1:].split()[0]] = i
        elif line.startswith('LABEL'): # Label
            jumper[line[6:]] = i

    # Second Pass
    while linePointer < len(lines):
        line = lines[linePointer]

        # Check if in skip area (function area).
        if line == "SSKP": inSkipArea += 1
        elif line == "ESKP": inSkipArea -= 1

        if inSkipArea > 0:
            linePointer += 1
            continue

        elif re.match(r"LDA .*", line):
            line = line[3:].strip()
            if typeOf(line) != "parameter": register.append(line)
            else: register.append(memory[variableStack[-1][line].address])

        elif re.match(r"LDAA .*", line):
            line = line[4:].strip().split()
            variableName = line.pop(0)

            for i, position in enumerate(line):
                if position == "_": line[i] = int(register.pop())
                else: line[i] = int(line[i])
            line = line[::-1]

            position = sum([x * y for x, y in zip(line[:-1], variableStack[-1][variableName].shape)]) + line[-1]

            register.append(memory[variableStack[-1][variableName].address][position])

        elif re.match(r"STA .*", line):
            variableName = line[3:].strip()
            memory[variableStack[-1][variableName].address] = register.pop()

        elif re.match(r"STAA .*", line):
            line = line[4:].strip().split()
            variableName = line.pop(0)

            for i, position in enumerate(line):
                if position == "_": line[i] = int(register.pop())
                else: line[i] = int(line[i])
            line = line[::-1]

            position = sum([x * y for x, y in zip(line[:-1], variableStack[-1][variableName].shape)]) + line[-1]

            memory[variableStack[-1][variableName].address][position] = register.pop()

        elif re.match(r"((INT )|(FLOAT )|(STR )|(BOOL )).*", line):
            address = addressGenerator()
            variableType, variableName, value = stringSpliter(line)
            
            if value == "_": value = register.pop()

            memory[address] = value
            variableStack[-1][variableName] = VariableType(variableType, address)

        elif re.match(r"((INTA )|(FLOATA )|(STRA )|(BOOLA )).*", line):
            address = addressGenerator()
            line = stringSpliter(line)
            variableType, variableName = line[0], line[1]
            line = line[2:]

            temp = []
            for i in line: temp.append(int(register.pop()) if i == "_" else int(i))

            length = 1
            for i in temp: length *= i

            initial = []
            if variableType == "INTA": initial = [0] * length
            elif variableType == "FLOATA": initial = [0.0] * length
            elif variableType == "STRA": initial = [""] * length
            elif variableType == "BOOLA": initial = ["false"] * length

            memory[address] = initial
            variableStack[-1][variableName] = VariableType(variableType, address, shape=temp)

        elif re.match(r"ADD .*", line):
            a, b = register.pop(), register.pop()
            ta, tb = typeOf(a), typeOf(b)
            if ta == "string" or tb == "string": temp = str(autoConvert(b)) + str(autoConvert(a))
            else: temp = autoConvert(b) + autoConvert(a)
            register.append(temp)

        elif re.match(r"SUB .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) - autoConvert(a)
            register.append(temp)

        elif re.match(r"MUL .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) * autoConvert(a)
            register.append(temp)

        elif re.match(r"DIV .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) / autoConvert(a)
            register.append(temp)

        elif re.match(r"EXP .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) ** autoConvert(a)
            register.append(temp)

        elif re.match(r"REM .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) % autoConvert(a)
            register.append(temp)

        elif re.match(r"EQL .*", line):
            a, b = register.pop(), register.pop()
            temp = bool(autoConvert(b) == autoConvert(a))
            register.append("true" if temp else "false")

        elif re.match(r"NEQ .*", line):
            a, b = register.pop(), register.pop()
            temp = bool(autoConvert(b) != autoConvert(a))
            register.append("true" if temp else "false")

        elif re.match(r"GRT .*", line):
            a, b = register.pop(), register.pop()
            temp = bool(autoConvert(b) > autoConvert(a))
            register.append("true" if temp else "false")

        elif re.match(r"LST .*", line):
            a, b = register.pop(), register.pop()
            temp = bool(autoConvert(b) < autoConvert(a))
            register.append("true" if temp else "false")

        elif re.match(r"GTE .*", line):
            a, b = register.pop(), register.pop()
            temp = bool(autoConvert(b) >= autoConvert(a))
            register.append("true" if temp else "false")

        elif re.match(r"LTE .*", line):
            a, b = register.pop(), register.pop()
            temp = bool(autoConvert(b) <= autoConvert(a))
            register.append("true" if temp else "false")

        elif re.match(r"BSL .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) >> autoConvert(a)
            register.append(temp)

        elif re.match(r"BSR .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) << autoConvert(a)
            register.append(temp)

        elif re.match(r"BAD .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) & autoConvert(a)
            register.append(temp)

        elif re.match(r"BXR .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) ^ autoConvert(a)
            register.append(temp)

        elif re.match(r"BOR .*", line):
            a, b = register.pop(), register.pop()
            temp = autoConvert(b) | autoConvert(a)
            register.append(temp)

        elif re.match(r"LAD .*", line):
            a, b = register.pop(), register.pop()
            temp = bool(autoConvert(b) and autoConvert(a))
            register.append("true" if temp else "false")

        elif re.match(r"LOR .*", line):
            a, b = register.pop(), register.pop()
            temp = bool(autoConvert(b) or autoConvert(a))
            register.append("true" if temp else "false")

        elif re.match(r"LNT .*", line):
            a = register.pop()
            temp = not bool(autoConvert(a))
            register.append("true" if temp else "false")

        elif re.match(r"MSG .*", line):
            line = line[3:].split()

            for i in line:
                if i == "_": print(register.pop())
                else: print(i)

        elif re.match(r"JMP ", line):
            condition, jumpToLabel = line[3:].split()

            if condition == "_": condition = register.pop()
            if autoConvert(condition):
                linePointer = int(jumper[jumpToLabel])
                continue

        elif re.match(r"CALL", line):
            line = line[4:].strip()
            
            returnStack.append(linePointer + 1)
            linePointer = int(jumper[line])
            continue

        elif re.match(r":", line):
            variableStack.append({})

        elif re.match(r"RET", line):
            variableStack.pop()
            linePointer = int(returnStack.pop())
            continue

        linePointer += 1

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
    # If there is no input assembly file, throw error.
    if len(sys.argv) < 2: error(0, "Input file has not been specified.")
    
    filename = sys.argv[1]
    if not os.path.isfile(filename): error(0, f"Input file {filename} not exists.")

    file = open(filename, "r").read()
    main(file)