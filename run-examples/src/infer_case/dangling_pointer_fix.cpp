#include <iostream>
#include <memory>

std::shared_ptr<int> create_safe() {
    return std::make_shared<int>(100); // 返回堆内存的智能指针
}

void use_safe() {
    auto p = create_safe();
    std::cout << "Safe value: " << *p << std::endl; // 安全访问
}