#include <iostream>
#include "dangling_pointer.h"

int *createInt(int defaultalue)
{
    int x = defaultalue;
    return &x;
}