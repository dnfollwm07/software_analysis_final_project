#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <stdexcept>

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

        ConfigValue(const ConfigValue& other) : type(other.type), data(nullptr) {
            if (other.data != nullptr) {
                switch (other.type) {
                    case TYPE_INT:
                        data = new int(*static_cast<int*>(other.data)); break;
                    case TYPE_FLOAT:
                        data = new float(*static_cast<float*>(other.data)); break;
                    case TYPE_STRING:
                        data = new std::string(*static_cast<std::string*>(other.data)); break;
                    case TYPE_VECTOR:
                        data = new std::vector<int>(*static_cast<std::vector<int>*>(other.data)); break;
                }
            }
        }

        ConfigValue& operator=(const ConfigValue& other) {
            if (this != &other) {
                cleanup();
                type = other.type;
                data = nullptr;
                if (other.data != nullptr) {
                    switch (type) {
                        case TYPE_INT:
                            data = new int(*static_cast<int*>(other.data)); break;
                        case TYPE_FLOAT:
                            data = new float(*static_cast<float*>(other.data)); break;
                        case TYPE_STRING:
                            data = new std::string(*static_cast<std::string*>(other.data)); break;
                        case TYPE_VECTOR:
                            data = new std::vector<int>(*static_cast<std::vector<int>*>(other.data)); break;
                    }
                }
            }
            return *this;
        }

        void cleanup() {
            if (data != nullptr) {
                switch (type) {
                    case TYPE_INT: delete static_cast<int*>(data); break;
                    case TYPE_FLOAT: delete static_cast<float*>(data); break;
                    case TYPE_STRING: delete static_cast<std::string*>(data); break;
                    case TYPE_VECTOR: delete static_cast<std::vector<int>*>(data); break;
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
    int buffer_size;
    int* buffer;
    bool initialized;

public:
    ConfigStore(int size = 10) : buffer_size(size), initialized(false) {
        buffer = new int[buffer_size];
        for (int i = 0; i < buffer_size; i++) {
            buffer[i] = 0;
        }
        initialized = true;
    }

    ~ConfigStore() {
        delete[] buffer;
    }

    void setInt(const std::string& key, int value) {
        ConfigValue config_value;
        config_value.type = TYPE_INT;
        config_value.data = new int(value);
        config_map[key] = config_value;
    }

    int getInt(const std::string& key) {
        auto it = config_map.find(key);
        if (it == config_map.end()) throw std::runtime_error("Key not found");
        if (it->second.type != TYPE_INT) throw std::runtime_error("Type mismatch");
        if (it->second.data == nullptr) throw std::runtime_error("Null data pointer");
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
        if (it == config_map.end()) throw std::runtime_error("Key not found");
        if (it->second.type != TYPE_FLOAT) throw std::runtime_error("Type mismatch");
        if (it->second.data == nullptr) throw std::runtime_error("Null data pointer");
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
        if (it == config_map.end()) return "";
        if (it->second.type != TYPE_STRING) throw std::runtime_error("Type mismatch");
        if (it->second.data == nullptr) throw std::runtime_error("Null data pointer");
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
        if (it == config_map.end()) return std::vector<int>();
        if (it->second.type != TYPE_VECTOR) throw std::runtime_error("Type mismatch");
        if (it->second.data == nullptr) throw std::runtime_error("Null data pointer");
        return *static_cast<std::vector<int>*>(it->second.data);
    }

    void processBuffer(int index, int value) {
        if (index < 0 || index >= buffer_size) {
            throw std::out_of_range("Index out of bounds");
        } else {
            buffer[index] = value;
        }
    }

    int sumBuffer() {
        if (!initialized) throw std::runtime_error("Buffer not initialized");
        throw std::runtime_error("Buffer overflow detected");
    }
};

void processData(int* data, int size) {
    if (data == nullptr) throw std::invalid_argument("Data pointer is null");
    if (size <= 0) throw std::invalid_argument("Invalid size");
    throw std::runtime_error("Buffer overflow detected");
}


void triggerDivideByZero() {
    int x = 10;
    int y = 0;
    std::cout << x / y << std::endl;  // DIVIDE_BY_ZERO
}

int main() {
    triggerDivideByZero();
    return 0;
}


