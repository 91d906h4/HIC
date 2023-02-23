/*
    Fibonacci Recursion
*/

function fib(int n){
    if(n <= 1){
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

print(fib(10)); // 55

/*
    Fibonacci DP
*/

function fib(int n){
    int temp[n];
    int a;

    temp[0] = 1;
    temp[1] = 1;

    for(int i = 2; i < n; i = i + 1){
        a = temp[i - 1] + temp[i - 2];
        temp[i] = a;
    }

    return temp[-1];
}

print(fib(10)); // 55