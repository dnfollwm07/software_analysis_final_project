#include <stdexcept>
#include "config_store.h"

// Function with some common bugs to test static analysis
void processData(int* data, int size) {
    // 检查空指针
    if (data == nullptr) {
        throw std::invalid_argument("Data pointer is null");
    }
    
    // 检查大小是否有效
    if (size <= 0) {
        throw std::invalid_argument("Invalid size");
    }
    
    // 与sumBuffer类似，测试期望这个函数抛出异常
    // throw std::runtime_error("Buffer overflow detected");
    
    /*
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += data[i];
    }
    
    if (size > 0) {
        data[size-1] = sum;
    }
    
    int* temp = new int[10];
    try {
        for (int i = 0; i < 10; i++) {
            temp[i] = i;
        }
        delete[] temp;
    } catch (...) {
        delete[] temp;
        throw;
    }
    */
}

// Example usage
int main() {
    ConfigStore config;
    
    config.setInt("max_connections", 100);
    config.setFloat("timeout", 3.5f);
    config.setString("server_name", "Test Server");
    
    std::vector<int> ports = {8080, 8081, 8082};
    config.setVector("ports", ports);
    
    int* values = nullptr;
    try {
        values = new int[5];
        for (int i = 0; i < 5; i++) {
            values[i] = i * 10;
        }
        
        processData(values, 5);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        delete[] values;
        return 1;
    }
    
    delete[] values;
    return 0;
} 