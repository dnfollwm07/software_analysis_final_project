#include <iostream>

void use_uninitialized() {
    int x; // 未初始化
    std::cout << "Garbage value: " << x << std::endl; // 输出随机值
}