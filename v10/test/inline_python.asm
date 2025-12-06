SYMBOL_TABLE {"angle": 0, "code": 1}
JMP L1
L1:
PUSH 0
STORE_GLOBAL 0
PUSH 0.0
STORE 0
PUSH 0
STORE_GLOBAL 1
STRING_NEW "\nimport math\nprint(f"Python internal: angle = {angle}")\nans = math.cos(angle)\nangle = 3.14159\n"
STORE 1
LOAD 1
EXEC_PYTHON
STRING_NEW "From HIC: ans = "
LOAD_PYTHON_GLOBAL "ans"
STR
ADD
PRINT
STRING_NEW "From HIC: angle updated = "
LOAD 0
STR
ADD
PRINT
HALT
