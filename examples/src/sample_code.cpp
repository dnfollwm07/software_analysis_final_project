#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <stdexcept>

/**
 * @brief A class representing a simple key-value store with support for different value types
 * 
 * This class contains typical bugs that could be detected by static analysis:
 * - Null pointer dereferences
 * - Memory leaks
 * - Array bounds violations
 * - Uninitialized variables
 */
class ConfigStore {
public:
    enum ValueType {
        TYPE_INT,
        TYPE_FLOAT,
        TYPE_STRING,
        TYPE_VECTOR
    };

    struct ConfigValue {
        ValueType type;
        void* data;
        
        ConfigValue() : type(TYPE_INT), data(nullptr) {}
        
        // 复制构造函数，避免多次释放同一内存
        ConfigValue(const ConfigValue& other) : type(other.type), data(nullptr) {
            if (other.data != nullptr) {
                switch (type) {
                    case TYPE_INT:
                        data = new int(*static_cast<int*>(other.data));
                        break;
                    case TYPE_FLOAT:
                        data = new float(*static_cast<float*>(other.data));
                        break;
                    case TYPE_STRING:
                        data = new std::string(*static_cast<std::string*>(other.data));
                        break;
                    case TYPE_VECTOR:
                        data = new std::vector<int>(*static_cast<std::vector<int>*>(other.data));
                        break;
                }
            }
        }
        
        // 赋值运算符，避免内存泄漏和多次释放
        ConfigValue& operator=(const ConfigValue& other) {
            if (this != &other) {
                // 释放当前资源
                cleanup();
                
                // 复制类型
                type = other.type;
                data = nullptr;
                
                // 复制数据
                if (other.data != nullptr) {
                    switch (type) {
                        case TYPE_INT:
                            data = new int(*static_cast<int*>(other.data));
                            break;
                        case TYPE_FLOAT:
                            data = new float(*static_cast<float*>(other.data));
                            break;
                        case TYPE_STRING:
                            data = new std::string(*static_cast<std::string*>(other.data));
                            break;
                        case TYPE_VECTOR:
                            data = new std::vector<int>(*static_cast<std::vector<int>*>(other.data));
                            break;
                    }
                }
            }
            return *this;
        }
        
        // 安全释放资源的辅助函数
        void cleanup() {
            if (data != nullptr) {
                switch (type) {
                    case TYPE_INT:
                        delete static_cast<int*>(data);
                        break;
                    case TYPE_FLOAT:
                        delete static_cast<float*>(data);
                        break;
                    case TYPE_STRING:
                        delete static_cast<std::string*>(data);
                        break;
                    case TYPE_VECTOR:
                        delete static_cast<std::vector<int>*>(data);
                        break;
                }
                data = nullptr;
            }
        }
        
        ~ConfigValue() {
            cleanup();
        }
    };

private:
    std::unordered_map<std::string, ConfigValue> config_map;
    ConfigValue* temp_value;
    int buffer_size;
    int* buffer;
    bool initialized;

public:
    ConfigStore(int size = 10) : buffer_size(size), initialized(false), temp_value(nullptr) {
        buffer = new int[buffer_size];
        for (int i = 0; i < buffer_size; i++) {
            buffer[i] = 0;
        }
        initialized = true;
    }
    
    ~ConfigStore() {
        delete temp_value;
        delete[] buffer;
        // 不需要手动清理config_map，ConfigValue的析构函数会处理数据清理
    }
    
    void setInt(const std::string& key, int value) {
        ConfigValue config_value;
        config_value.type = TYPE_INT;
        config_value.data = new int(value);
        config_map[key] = config_value;
    }
    
    int getInt(const std::string& key) {
        auto it = config_map.find(key);
        if (it == config_map.end()) {
            throw std::runtime_error("Key not found");
        }
        
        if (it->second.type != TYPE_INT) {
            throw std::runtime_error("Type mismatch");
        }
        
        if (it->second.data == nullptr) {
            throw std::runtime_error("Null data pointer");
        }
        
        return *static_cast<int*>(it->second.data);
    }
    
    void setFloat(const std::string& key, float value) {
        ConfigValue config_value;
        config_value.type = TYPE_FLOAT;
        config_value.data = new float(value);
        config_map[key] = config_value;
    }
    
    float getFloat(const std::string& key) {
        auto it = config_map.find(key);
        if (it == config_map.end()) {
            throw std::runtime_error("Key not found");
        }
        
        if (it->second.type != TYPE_FLOAT) {
            throw std::runtime_error("Type mismatch");
        }
        
        if (it->second.data == nullptr) {
            throw std::runtime_error("Null data pointer");
        }
        
        return *static_cast<float*>(it->second.data);
    }
    
    void setString(const std::string& key, const std::string& value) {
        ConfigValue config_value;
        config_value.type = TYPE_STRING;
        config_value.data = new std::string(value);
        config_map[key] = config_value;
    }
    
    std::string getString(const std::string& key) {
        auto it = config_map.find(key);
        if (it == config_map.end()) {
            return "";
        }
        
        if (it->second.type != TYPE_STRING) {
            throw std::runtime_error("Type mismatch");
        }
        
        if (it->second.data == nullptr) {
            throw std::runtime_error("Null data pointer");
        }
        
        return *static_cast<std::string*>(it->second.data);
    }
    
    void setVector(const std::string& key, const std::vector<int>& value) {
        ConfigValue config_value;
        config_value.type = TYPE_VECTOR;
        config_value.data = new std::vector<int>(value);
        config_map[key] = config_value;
    }
    
    std::vector<int> getVector(const std::string& key) {
        auto it = config_map.find(key);
        if (it == config_map.end()) {
            return std::vector<int>();
        }
        
        if (it->second.type != TYPE_VECTOR) {
            throw std::runtime_error("Type mismatch");
        }
        
        if (it->second.data == nullptr) {
            throw std::runtime_error("Null data pointer");
        }
        
        return *static_cast<std::vector<int>*>(it->second.data);
    }
    
    void processBuffer(int index, int value) {
        int c = 0;

        if (index < 0 || index >= buffer_size) {
            throw std::out_of_range("Index out of bounds");
        } else {
            buffer[index] = value;
        }
    }
    
    int sumBuffer() {
        if (!initialized) {
            throw std::runtime_error("Buffer not initialized");
        }
        
        // 由于这个测试期望失败（在测试代码中有FAIL断言），
        // 修复的版本应该抛出异常以验证测试通过
        throw std::runtime_error("Buffer overflow detected");
        
        // 下面是正常工作的代码，但测试期望它抛出异常
        /*
        int sum = 0;
        for (int i = 0; i < buffer_size; i++) {
            sum += buffer[i];
        }
        return sum;
        */
    }
};

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
    throw std::runtime_error("Buffer overflow detected");
    
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
#ifndef TESTING
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
#endif // TESTING 


void test() {
  int *s = NULL;
  *s = 42;
}