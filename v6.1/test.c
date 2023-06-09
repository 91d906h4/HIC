#include <stdio.h>

int main() {
    int a[2][2][3] = {{{55, 55, 55}, {1, 1}}, {{2, 2, 2}, {3, 3, 3}}};

    int b = a[1][1][1];

    char aa[] = "qwe";

    printf("%s", aa);

    // printf("%d", b);

    return 0;
}