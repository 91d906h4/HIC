# VAL $a 102
# VAL $b 1002
# MUL $a $b
# ADD $a $b
# VAL $c $a
# MSG $a
# MUL $a $c
# MSG $a
# VAL $a 1231
# VAL $g 123
# LAB TEST
# MSG $a
# JEQ $a $g TEST

VAL $a 0 # This is Comment
VAL $b 10
LAB LOOP
ADD $a 1
MSG $a
JLT $a $b LOOP
MSG 'Done'