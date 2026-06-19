/*
    A tour of arrays, strings, loops, and operators.
*/

// Fill an array with the first eight square numbers.
int squares[8];
for(int i = 0; i < 8; i = i + 1){
    squares[i] = i * i;
}
print(squares);        // [0, 1, 4, 9, 16, 25, 36, 49]
print(squares[-1]);    // 49  (negative index counts from the end)

// Strings concatenate with '+'.
string greeting = "Hello" + ", " + "world" + "!";
print(greeting);       // Hello, world!

// Operator precedence, bit shifts, modulo, and booleans.
int x = 8 + 5 * 2;
print(x);              // 18
print(1 << 4);         // 16
print(7 % 3 == 1);     // true
print(not false and true);   // true
