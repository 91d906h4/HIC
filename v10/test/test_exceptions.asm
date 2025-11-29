JMP L1
L1:
STRING_NEW "Test 1: Basic try/catch"
PRINT
PUSH 0
TRY_BEGIN L2
STRING_NEW "In try block"
PRINT
PUSH 0
STRING_NEW "Something went wrong!"
THROW
STRING_NEW "This should not print"
PRINT
PUSH 0
TRY_END
JMP L3
L2:
STRING_NEW "Caught exception!"
PRINT
PUSH 0
L3:
STRING_NEW "Test 2: No exception"
PRINT
PUSH 0
TRY_BEGIN L4
STRING_NEW "No error here"
PRINT
PUSH 0
TRY_END
JMP L5
L4:
STRING_NEW "This should not print"
PRINT
PUSH 0
L5:
STRING_NEW "Test 3: Nested try/catch"
PRINT
PUSH 0
TRY_BEGIN L6
STRING_NEW "Outer try"
PRINT
PUSH 0
TRY_BEGIN L8
STRING_NEW "Inner try"
PRINT
PUSH 0
STRING_NEW "Inner error"
THROW
TRY_END
JMP L9
L8:
STRING_NEW "Inner catch"
PRINT
PUSH 0
L9:
STRING_NEW "After inner try/catch"
PRINT
PUSH 0
TRY_END
JMP L7
L6:
STRING_NEW "Outer catch - should not reach"
PRINT
PUSH 0
L7:
STRING_NEW "All tests completed"
PRINT
PUSH 0
HALT
