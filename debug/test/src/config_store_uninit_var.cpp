#include "config_store_uninit_var.h"

// ConfigValue implementation
ConfigStoreUninitVar::ConfigValue::ConfigValue() : type(TYPE_INT), data(nullptr) {}

ConfigStoreUninitVar::ConfigValue::ConfigValue(const ConfigValue& other) : type(other.type), data(nullptr) {
    if (other.data != nullptr) {
        switch (other.type) {
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

ConfigStoreUninitVar::ConfigValue& ConfigStoreUninitVar::ConfigValue::operator=(const ConfigValue& other) {
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

void ConfigStoreUninitVar::ConfigValue::cleanup() {
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

ConfigStoreUninitVar::ConfigValue::~ConfigValue() {
    cleanup();
}

// ConfigStoreUninitVar implementation
ConfigStoreUninitVar::ConfigStoreUninitVar(int size) : buffer_size(size), initialized(false) {
    buffer = new int[buffer_size];
    for (int i = 0; i < buffer_size; i++) {
        buffer[i] = 0;
    }
    initialized = true;
}

ConfigStoreUninitVar::~ConfigStoreUninitVar() {
    delete[] buffer;
    // 不需要手动清理config_map，ConfigValue的析构函数会处理数据清理
}

void ConfigStoreUninitVar::setInt(const std::string& key, int value) {
    ConfigValue config_value;
    config_value.type = TYPE_INT;
    config_value.data = new int(value);
    config_map[key] = config_value;
}

int ConfigStoreUninitVar::getInt(const std::string& key) {
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

void ConfigStoreUninitVar::setFloat(const std::string& key, float value) {
    ConfigValue config_value;
    config_value.type = TYPE_FLOAT;
    config_value.data = new float(value);
    config_map[key] = config_value;
}

float ConfigStoreUninitVar::getFloat(const std::string& key) {
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

void ConfigStoreUninitVar::setString(const std::string& key, const std::string* value) {
    if (value == nullptr || value->empty()) {
        return;
    }
    ConfigValue config_value;
    config_value.type = TYPE_STRING;
    config_value.data = new std::string(*value);
    config_map[key] = config_value;
}

std::string ConfigStoreUninitVar::getString(const std::string& key) {
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

void ConfigStoreUninitVar::setVector(const std::string& key, const std::vector<int>& value) {
    ConfigValue config_value;
    config_value.type = TYPE_VECTOR;
    config_value.data = new std::vector<int>(value);
    config_map[key] = config_value;
}

std::vector<int> ConfigStoreUninitVar::getVector(const std::string& key) {
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

void ConfigStoreUninitVar::processBuffer(int index, int value) {
    int c = 0;

    if (index < 0 || index >= buffer_size) {
        throw std::out_of_range("Index out of bounds");
    } else {
        buffer[index] = value;
    }
}

int ConfigStoreUninitVar::sumBuffer(int start, int end) {
    if (!initialized) {
        throw std::runtime_error("Buffer not initialized");
    }

    if (start < 0 || start > end) {
        throw std::out_of_range("Invalid range");
    }

    if (end > buffer_size) {
        throw std::runtime_error("Buffer overflow detected");
    }
    int sum = 0; // Fix: Initialize sum to 0
    for (int i = start; i < end; i++) {
        sum += buffer[i];
    }
    return sum;
}