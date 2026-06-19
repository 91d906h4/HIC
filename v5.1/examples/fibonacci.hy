/*
    Fibonacci numbers, two ways.
*/

// Naive recursion.
function fib(int n){
    if(n <= 1){
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

// Bottom-up dynamic programming using an array.
function fib_dp(int n){
    int table[n + 1];
    table[0] = 0;
    table[1] = 1;
    for(int i = 2; i <= n; i = i + 1){
        table[i] = table[i - 1] + table[i - 2];
    }
    return table[n];
}

print(fib(10));      // 55
print(fib_dp(10));   // 55
