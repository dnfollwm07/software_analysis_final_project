#include "vector_invalid.h"
#include <vector>
#include <iostream>

int pushReturnHead(std::vector<int> &vec)
{

  int *elt = &vec[1];
  int *y = elt;
  vec.push_back(100);
  int result = *y;
  return result;
}

int myFunc(int a, int b)
{
  std::vector<int> vec;
  vec.push_back(a);
  vec.push_back(b);
  return pushReturnHead(vec);
}