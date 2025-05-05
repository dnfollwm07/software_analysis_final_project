#include "uninit_var.h"
#include <vector>

static int processLevel3(int value, int mod)
{
    int v;
    if (v % 2 == 0)
    {
        v = 1;
    }

    return (value + v) - mod;
}

static int processLevel2(int value)
{
    int modifier;

    if (value > 100)
    {
        modifier = 5;
    }
    return processLevel3(value, modifier);
}

static int processLevel1(int input)
{
    return processLevel2(input * 2);
}

int myCalculate(int input)
{
    int temp;
    if (input > 0)
    {
        temp += processLevel1(input + 5);
    }
    else
    {
        temp += processLevel1(input);
    }
    return temp;
}