#include "uninit_var.h"
#include <vector>

static int processLevel3(int value, int mod)
{
    // FIXME: 未初始化 int v = 0;
    int v;
    if (v % 2 == 0)
    {
        v = 1;
    }

    return (value + v) - mod;
}

static int processLevel2(int value)
{
    // FIXME: 未初始化  int modifier = 0;
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
    // FIXME: 未初始化 int temp = 0;
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