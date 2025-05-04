// config_store_bug.cpp

#include "config_store.h"
#include <stdexcept>
#include <sstream>
#include <string>
#include <vector>
#include <map>

// Internal storage
std::map<std::string, std::string> string_values;
std::map<std::string, std::vector<int>> vector_values;
int buffer[10];  // Fixed-size buffer

//Bug 1: No exception thrown when key is missing → NonexistentInt, NonexistentFloat should fail
int ConfigStore::getInt(const std::string& key) {
    return std::stoi(string_values[key]);  // ❌ If key is missing, returns empty string → std::stoi("") → exception or invalid value
}
float ConfigStore::getFloat(const std::string& key) {
    return std::stof(string_values[key]);  // ❌ same issue
}

std::string ConfigStore::getString(const std::string& key) {
    return string_values[key];
}

std::vector<int> ConfigStore::getVector(const std::string& key) {
    return vector_values[key];
}

void ConfigStore::setInt(const std::string& key, int value) {
    string_values[key] = std::to_string(value);
}

void ConfigStore::setFloat(const std::string& key, float value) {
    string_values[key] = std::to_string(value);
}

void ConfigStore::setString(const std::string& key, const std::string& value) {
    string_values[key] = value;
}

void ConfigStore::setVector(const std::string& key, const std::vector<int>& vec) {
    vector_values[key] = vec;
}

// ✅ Bug 2: No exception on type mismatch → TypeMismatchInt should fail
// Currently, no exception is thrown → std::stoi handles it automatically (may fail silently)

void ConfigStore::processBuffer(int index, int value) {
      // ✅ Bug 3: No bounds check → BufferProcessingOutOfBounds should fail
   buffer[index] = value; // ❌ Access beyond index 9 causes out-of-bounds write
}

int ConfigStore::sumBuffer() {
// ✅ Bug 4: Out-of-bounds read + uninitialized access → SumBuffer should fail
    int sum = 0;
    for (int i = 0; i < 20; ++i) { // ❌ Buffer only has 10 elements, reading beyond that is invalid
        sum += buffer[i];           // ❌ Reading uninitialized memory
        }
    return sum;
}



// ConfigStore 생성자
ConfigStore::ConfigStore(int size) {
    buffer_size = size;
    buffer = nullptr;
    initialized = false;
}

// ConfigStore 소멸자
ConfigStore::~ConfigStore() {
    delete[] buffer;
}

// ConfigValue cleanup 구현
void ConfigStore::ConfigValue::cleanup() {
    if (data != nullptr) {
        switch (type) {
            case TYPE_INT:
                delete static_cast<int*>(data); break;
            case TYPE_FLOAT:
                delete static_cast<float*>(data); break;
            case TYPE_STRING:
                delete static_cast<std::string*>(data); break;
            case TYPE_VECTOR:
                delete static_cast<std::vector<int>*>(data); break;
        }
        data = nullptr;
    }
}

// ConfigValue 소멸자
ConfigStore::ConfigValue::~ConfigValue() {
    cleanup();
}

