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
        
        ~ConfigValue() {
            // BUG: Missing proper cleanup for different types
            // This will cause memory leaks
            if (type == TYPE_STRING && data != nullptr) {
                delete static_cast<std::string*>(data);
            }
            // BUG: Missing cleanup for vector type
        }
    };

private:
    std::unordered_map<std::string, ConfigValue> config_map;
    ConfigValue* temp_value; // BUG: Potential memory leak
    int buffer_size;
    int* buffer; // BUG: Potential null pointer dereference
    bool initialized;

public:
    ConfigStore(int size = 10) : buffer_size(size), initialized(false) {
        // BUG: Missing initialization of temp_value
        buffer = new int[buffer_size];
        // Initialize buffer values
        for (int i = 0; i < buffer_size; i++) {
            buffer[i] = 0;
        }
        // BUG: Missing initialization of buffer values
        
        // BUG: initialized is set to false and never changed
    }
    
    ~ConfigStore() {
        // BUG: Missing delete for temp_value
        delete[] buffer;
        
        for (auto& pair : config_map) {
            // BUG: Missing cleanup for different types
            if (pair.second.type == TYPE_VECTOR && pair.second.data != nullptr) {
                delete static_cast<std::vector<int>*>(pair.second.data);
            }
            // Missing cleanup for other types is handled incorrectly in ConfigValue destructor
        }
    }
    
    void setInt(const std::string& key, int value) {
        ConfigValue config_value;
        config_value.type = TYPE_INT;
        config_value.data = new int(value); // BUG: Memory leak if key already exists
        config_map[key] = config_value;
    }
    
    int getInt(const std::string& key) {
        if (config_map.find(key) == config_map.end()) {
            // BUG: Returning uninitialized value
            return *buffer; // BUG: May access uninitialized memory
        }
        
        ConfigValue& value = config_map[key];
        if (value.type != TYPE_INT) {
            throw std::runtime_error("Type mismatch");
        }
        
        if (value.data == nullptr) {
            // BUG: Returning from nullptr
            return 0;
        }
        
        return *static_cast<int*>(value.data);
    }
    
    void setFloat(const std::string& key, float value) {
        ConfigValue config_value;
        config_value.type = TYPE_FLOAT;
        config_value.data = new float(value); // BUG: Memory leak if key already exists
        config_map[key] = config_value;
    }
    
    float getFloat(const std::string& key) {
        if (config_map.find(key) == config_map.end()) {
            // BUG: Returning uninitialized value
            float default_value = 0.0f; // BUG: Uninitialized variable
            return default_value;
        }
        
        ConfigValue& value = config_map[key];
        if (value.type != TYPE_FLOAT) {
            throw std::runtime_error("Type mismatch");
        }
        
        return *static_cast<float*>(value.data);
    }
    
    void setString(const std::string& key, const std::string& value) {
        ConfigValue config_value;
        config_value.type = TYPE_STRING;
        config_value.data = new std::string(value);
        config_map[key] = config_value;
    }
    
    std::string getString(const std::string& key) {
        if (config_map.find(key) == config_map.end()) {
            return "";
        }
        
        ConfigValue& value = config_map[key];
        if (value.type != TYPE_STRING) {
            throw std::runtime_error("Type mismatch");
        }
        
        return *static_cast<std::string*>(value.data);
    }
    
    void setVector(const std::string& key, const std::vector<int>& value) {
        ConfigValue config_value;
        config_value.type = TYPE_VECTOR;
        config_value.data = new std::vector<int>(value);
        config_map[key] = config_value;
    }
    
    std::vector<int> getVector(const std::string& key) {
        if (config_map.find(key) == config_map.end()) {
            return std::vector<int>();
        }
        
        ConfigValue& value = config_map[key];
        if (value.type != TYPE_VECTOR) {
            throw std::runtime_error("Type mismatch");
        }
        
        return *static_cast<std::vector<int>*>(value.data);
    }
    
    // BUG: Array bounds violation potential
    void processBuffer(int index, int value) {
        if (index >= 0 && index < buffer_size) { // BUG: Missing upper bound check
            buffer[index] = value;
        } else {
            throw std::out_of_range("Index out of bounds");
        }
    }
    
    // BUG: Using uninitialized buffer
    int sumBuffer() {
        int sum = 0;
        for (int i = 0; i < buffer_size; i++) { // BUG: Off-by-one error
            sum += buffer[i];
        }
        return sum;
    }
};

// Function with some common bugs to test static analysis
void processData(int* data, int size) {
    // Add null check
    if (data == nullptr) {
        throw std::invalid_argument("Data pointer is null");
    }
    // BUG: Missing null check on data
    int sum = 0;
    
    // BUG: Potential overflow
    for (int i = 0; i <= size; i++) { // Off-by-one error
        sum += data[i];
    }
    
    // BUG: Out of bounds access
    if (size > 0) {
        data[size] = sum; // Out of bounds write
    }
    
    // BUG: Memory leak
    int* temp = new int[10];
    for (int i = 0; i < 10; i++) {
        temp[i] = i;
    }
    // Missing delete[] temp
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
    
    // BUG: Potential null pointer dereference
    int* values = nullptr;
    try {
        // BUG: Memory leak if exception thrown
        values = new int[5];
        processData(values, 5); // Undefined behavior due to bugs in processData
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        // Missing delete[] values
        return 1;
    }
    
    delete[] values;
    return 0;
}
#endif 