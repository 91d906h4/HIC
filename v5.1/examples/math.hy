/*
    Using an imported module. Arguments bind left-to-right:
    pow(base, exp) computes base ** exp.
*/

#import <math.hm>

int base = 2;
int exponent = 10;

print(abs(-100));               // 100
print(pow(base, exponent));     // 1024
print(max(base, exponent));     // 10
