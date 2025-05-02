#include <iostream>
#include <memory>

void no_leak() {
    auto ptr = std::make_unique<int>(42);
    std::cout << "Safe value: " << *ptr << std::endl;
    // unique_ptr 自动释放内存，无需手动 delete
}