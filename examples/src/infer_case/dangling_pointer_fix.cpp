#include <iostream>
#include <memory>

std::shared_ptr<int> create_dangling() {
    return std::make_shared<int>(100); // 返回堆内存的智能指针
}

void use_dangling() {
    auto p = create_dangling();
    std::cout << "Safe value: " << *p << std::endl; // 安全访问
}