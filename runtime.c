#include <stdio.h>

double input_var(const char *name) {
    double value;
    printf("Input %s: ", name);
    scanf("%lf", &value);
    return value;
}
