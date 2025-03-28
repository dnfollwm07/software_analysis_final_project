#define TESTING 1

#include <iostream>
#include <cassert>
#include <string>
#include <vector>
#include <memory>
#include <functional>

// 根據TEST_CORRECT變量決定包含哪個版本的代碼
#ifdef TEST_CORRECT
#include "../src/correct_code.cpp"
#else
#include "../src/test_code.cpp"
#endif

/**
 * Simple test framework for ConfigStore
 * 
 * This test suite aims to test both correct and buggy implementations
 * of the ConfigStore class.
 */

// Utility function to check if a specific test passes
bool runTest(const std::string& test_name, std::function<bool()> test_func) {
    std::cout << "Running test: " << test_name << "... ";
    bool result = false;
    
    try {
        result = test_func();
        if (result) {
            std::cout << "PASSED" << std::endl;
        } else {
            std::cout << "FAILED" << std::endl;
        }
    } catch (const std::exception& e) {
        std::cout << "EXCEPTION: " << e.what() << std::endl;
        result = false;
    } catch (...) {
        std::cout << "UNKNOWN EXCEPTION" << std::endl;
        result = false;
    }
    
    return result;
}

// Test for basic integer storage and retrieval
bool testIntStorage() {
    ConfigStore config;
    config.setInt("test_key", 42);
    int value = config.getInt("test_key");
    return value == 42;
}

// Test for basic float storage and retrieval
bool testFloatStorage() {
    ConfigStore config;
    config.setFloat("test_key", 3.14f);
    float value = config.getFloat("test_key");
    return std::abs(value - 3.14f) < 0.001f;
}

// Test for basic string storage and retrieval
bool testStringStorage() {
    ConfigStore config;
    config.setString("test_key", "test_value");
    std::string value = config.getString("test_key");
    return value == "test_value";
}

// Test for basic vector storage and retrieval
bool testVectorStorage() {
    ConfigStore config;
    std::vector<int> test_vec = {1, 2, 3, 4, 5};
    config.setVector("test_key", test_vec);
    std::vector<int> value = config.getVector("test_key");
    return value == test_vec;
}

// Test for nonexistent key access (int)
bool testNonexistentInt() {
    ConfigStore config;
    try {
        int value = config.getInt("nonexistent");
        // For buggy implementation: we can't verify the value because it's reading from uninitialized memory
        // For correct implementation: should return 0 as default
        #ifdef TEST_CORRECT
        return value == 0;
        #else
        return false;
        #endif
    } catch (const std::exception& e) {
        // For fixed implementation that throws
        return true;
    }
}

// Test for nonexistent key access (float)
bool testNonexistentFloat() {
    ConfigStore config;
    try {
        float value = config.getFloat("nonexistent");
        // For buggy implementation: uninitialized value
        // For correct implementation: should return 0.0f as default
        #ifdef TEST_CORRECT
        return value == 0.0f;
        #else
        return false;
        #endif
    } catch (const std::exception& e) {
        // For fixed implementation that throws
        return true;
    }
}

// Test for type mismatch in getInt
bool testTypeMismatchInt() {
    ConfigStore config;
    config.setString("test_key", "not_an_int");
    try {
        int value = config.getInt("test_key");
        return false; // Should not reach here
    } catch (const std::runtime_error& e) {
        return std::string(e.what()) == "Type mismatch";
    }
}

// Test for buffer processing with in-bounds index
bool testBufferProcessing() {
    ConfigStore config;
    try {
        config.processBuffer(5, 42); // Should be in bounds for default buffer size (10)
        return true;
    } catch (const std::exception& e) {
        return false;
    }
}

// Test for buffer processing with out-of-bounds index
bool testBufferProcessingOutOfBounds() {
    ConfigStore config;
    try {
        // This should fail due to missing upper bound check in buggy implementation
        config.processBuffer(15, 42); // Out of bounds for default buffer size (10)
        #ifdef TEST_CORRECT
        return false; // Should not reach here in correct implementation
        #else
        return false; // Should not reach here if buggy implementation is fixed
        #endif
    } catch (const std::out_of_range& e) {
        return true; // Expected exception
    }
}

// Test for memory leaks in set methods
bool testMemoryLeakOnOverwrite() {
    // This test can't directly verify memory leaks, but can help 
    // manual verification with tools like Valgrind
    ConfigStore config;
    config.setInt("test_key", 42);
    config.setInt("test_key", 43); // Overwrite should clean up old value
    return config.getInt("test_key") == 43;
}

// Test for sumBuffer method
bool testSumBuffer() {
    ConfigStore config;
    try {
        int sum = config.sumBuffer();
        #ifdef TEST_CORRECT
        // In correct implementation, all buffer values are 0, so sum should be 0
        return sum == 0;
        #else
        // In buggy implementation, we have uninitialized values and off-by-one error
        return false;
        #endif
    } catch (const std::exception& e) {
        // If the implementation detects and throws for out of bounds
        return true;
    }
}

// Test for processData function
bool testProcessData() {
    int data[5] = {1, 2, 3, 4, 5};
    try {
        processData(data, 5);
        #ifdef TEST_CORRECT
        // Correct implementation should compute sum and store it in the last element
        return data[4] == 15;
        #else
        // Buggy implementation would cause undefined behavior
        return false;
        #endif
    } catch (const std::exception& e) {
        // Fixed buggy implementation might detect and handle errors
        return true;
    }
}

// Test for null pointer handling in processData
bool testProcessDataNullPtr() {
    try {
        processData(nullptr, 5);
        #ifdef TEST_CORRECT
        return false; // Should throw in correct implementation
        #else
        return false; // Buggy implementation doesn't check for null
        #endif
    } catch (const std::exception& e) {
        // Correct implementation should detect null pointer
        return true;
    }
}

int main() {
    int passed = 0;
    int total = 0;
    
    // Basic storage and retrieval tests
    total++; if (runTest("Integer Storage", testIntStorage)) passed++;
    total++; if (runTest("Float Storage", testFloatStorage)) passed++;
    total++; if (runTest("String Storage", testStringStorage)) passed++;
    total++; if (runTest("Vector Storage", testVectorStorage)) passed++;
    
    // Error case tests
    total++; if (runTest("Nonexistent Int Key", testNonexistentInt)) passed++;
    total++; if (runTest("Nonexistent Float Key", testNonexistentFloat)) passed++;
    total++; if (runTest("Type Mismatch", testTypeMismatchInt)) passed++;
    
    // Buffer processing tests
    total++; if (runTest("Buffer Processing", testBufferProcessing)) passed++;
    total++; if (runTest("Buffer Processing Out Of Bounds", testBufferProcessingOutOfBounds)) passed++;
    
    // Memory leak tests
    total++; if (runTest("Memory Leak On Overwrite", testMemoryLeakOnOverwrite)) passed++;
    
    // sumBuffer tests
    total++; if (runTest("Sum Buffer", testSumBuffer)) passed++;
    
    // processData tests
    total++; if (runTest("Process Data", testProcessData)) passed++;
    total++; if (runTest("Process Data Null Pointer", testProcessDataNullPtr)) passed++;
    
    std::cout << "\nTest summary: " << passed << " passed out of " << total << " tests." << std::endl;

    #ifdef TEST_CORRECT
    std::cout << "Testing CORRECT implementation." << std::endl;
    if (passed < total) {
        std::cout << "Some tests failed on the supposedly correct implementation!" << std::endl;
        return 1;
    } else {
        std::cout << "All tests passed on the correct implementation." << std::endl;
        return 0;
    }
    #else
    std::cout << "Testing BUGGY implementation." << std::endl;
    if (passed < total) {
        std::cout << "As expected, some tests failed on the buggy implementation." << std::endl;
        return 1;
    } else {
        std::cout << "Unexpectedly, all tests passed on the buggy implementation!" << std::endl;
        return 0;
    }
    #endif
} 