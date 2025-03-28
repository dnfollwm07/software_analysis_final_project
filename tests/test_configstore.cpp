#include <iostream>
#include <cassert>
#include <string>
#include <vector>
#include <memory>
#include "../src/sample_code.cpp"

/**
 * Simple test framework for ConfigStore
 * 
 * This test suite aims to trigger the bugs in the ConfigStore implementation
 * and validate that they are fixed after repair.
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
    // This test is expected to fail due to the bug with uninitialized buffer
    ConfigStore config;
    try {
        int value = config.getInt("nonexistent");
        // If we get here, the function didn't throw, but we can't verify the value
        // because it's reading from uninitialized memory
        return false;
    } catch (const std::exception& e) {
        // Expected behavior after fix would be to throw or return a default value
        return true;
    }
}

// Test for nonexistent key access (float)
bool testNonexistentFloat() {
    // This test is expected to fail due to the bug with uninitialized default_value
    ConfigStore config;
    try {
        float value = config.getFloat("nonexistent");
        // If we get here, the function didn't throw, but returned an uninitialized value
        return false;
    } catch (const std::exception& e) {
        // Expected behavior after fix would be to throw or return a default value
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
        // This should fail due to missing upper bound check
        config.processBuffer(15, 42); // Out of bounds for default buffer size (10)
        return false; // Should not reach here if checks are fixed
    } catch (const std::out_of_range& e) {
        return true; // Expected exception after fix
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
    // This test is expected to fail due to:
    // 1. Uninitialized buffer values
    // 2. Off-by-one error in the loop
    
    // After fix, it should initialize the buffer and fix the loop bounds
    ConfigStore config;
    try {
        int sum = config.sumBuffer();
        // We can't verify the sum value due to uninitialized buffer
        return false;
    } catch (const std::exception& e) {
        // If the fixed implementation detects and throws for out of bounds
        return true;
    }
}

// Test for processData function
bool testProcessData() {
    // This test checks the processData function for bugs:
    // - Null check
    // - Off-by-one error
    // - Out of bounds access
    // - Memory leaks
    
    int data[5] = {1, 2, 3, 4, 5};
    try {
        processData(data, 5);
        // Original implementation would cause undefined behavior
        return false;
    } catch (const std::exception& e) {
        // Fixed implementation should detect and handle errors
        return true;
    }
}

// Test for null pointer handling in processData
bool testProcessDataNullPtr() {
    try {
        processData(nullptr, 5);
        // Original implementation doesn't check for null
        return false;
    } catch (const std::exception& e) {
        // Fixed implementation should detect null pointer
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
    
    if (passed < total) {
        std::cout << "Note: Some tests are expected to fail before bugs are fixed." << std::endl;
        std::cout << "After successful repair, all tests should pass." << std::endl;
    }
    
    return (passed == total) ? 0 : 1;
} 