#include <iostream>

void safe_dereference(int* ptr) {
    if (ptr != nullptr) {
        std::cout << "Value: " << *ptr << std::endl;
    } else {
        std::cout << "Pointer is null!" << std::endl;
    }
}

int dereference_null_main() {
    int x = 42;
    safe_dereference(&x); // 输出 42
    safe_dereference(nullptr); // 输出警告
    return 0;
}