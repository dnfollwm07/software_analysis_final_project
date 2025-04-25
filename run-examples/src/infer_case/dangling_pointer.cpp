#include <iostream>

int* create_dangling() {
    int x = 100;
    return &x;
}

void use_dangling() {
    int* p = create_dangling();
    std::cout << "Dangling value: " << *p << std::endl; // 未定义行为！可能崩溃或输出垃圾值
}