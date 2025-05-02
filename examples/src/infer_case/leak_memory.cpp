#include <iostream>

void leak_memory() {
    int* ptr = new int(42);
    std::cout << "Leaked value: " << *ptr << std::endl; // 正常打印
    // 忘记 delete ptr; 导致内存泄漏
}