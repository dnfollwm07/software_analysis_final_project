#include <iostream>

void dereference_null(int* ptr) {
    if (ptr != nullptr) { // 添加空指针检查
        std::cout << "Value: " << *ptr << std::endl;
    } else {
        std::cout << "Pointer is null" << std::endl;
    }
}

int dereference_null_main() {
    int* p = nullptr;
    dereference_null(p); 
    return 0;
}