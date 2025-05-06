#include <iostream>
#include "dangling_pointer.h"

int *createInt(int defaultValue)
{
    int *x = new int(defaultValue);
    return x;
}