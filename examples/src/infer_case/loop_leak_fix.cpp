#include <iostream>
#include <vector>
#include <memory>

void no_loop_leak() {
    std::vector<std::unique_ptr<int>> pointers;
    for (int i = 0; i < 5; ++i) {
        auto ptr = std::make_unique<int>(i);
        std::cout << "Managed: " << *ptr << std::endl;
        pointers.push_back(std::move(ptr)); // 存储智能指针
    }
    // vector 销毁时自动释放所有内存
}