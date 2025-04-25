#include <iostream>

void loop_leak() {
    for (int i = 0; i < 5; ++i) {
        int* ptr = new int(i);
        std::cout << "Allocated: " << *ptr << std::endl;
        // 忘记 delete ptr; 导致每次循环泄漏 4 字节
    }
}