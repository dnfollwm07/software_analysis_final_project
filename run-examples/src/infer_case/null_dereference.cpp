#include <iostream>

void dereference_null(int* ptr) {
    std::cout << "Value: " << *ptr << std::endl; // 可能解引用空指针
}

int dereference_null_main() {
    int* p = nullptr;
    dereference_null(p); // 传递空指针
    return 0;
}