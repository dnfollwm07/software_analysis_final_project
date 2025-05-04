#include <gtest/gtest.h>
#include <iostream>
#include <cassert>
#include <string>
#include <vector>
#include <memory>
#include <functional>

// 定义TESTING宏，以便在包含sample_code.cpp时屏蔽其main函数
// #define TESTING
#include "../src/config_store.h"
using ConfigStoreImpl = ConfigStore;

/**
 * Google Test测试套件，用于测试ConfigStore实现
 * 
 * 这个测试套件旨在触发ConfigStore实现中的bug，
 * 并在修复后验证其正确性。
 */

class ConfigStoreTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 在每个测试前设置
    }

    void TearDown() override {
        // 在每个测试后清理
    }
};

// 测试基本整数存储和检索
TEST_F(ConfigStoreTest, IntStorage) {
    ConfigStoreImpl config;
    config.setInt("test_key", 42);
    int value = config.getInt("test_key");
    EXPECT_EQ(value, 42);
}

// 测试基本浮点数存储和检索
TEST_F(ConfigStoreTest, FloatStorage) {
    ConfigStoreImpl config;
    config.setFloat("test_key", 3.14f);
    float value = config.getFloat("test_key");
    EXPECT_NEAR(value, 3.14f, 0.001f);
}

// 测试基本字符串存储和检索
TEST_F(ConfigStoreTest, StringStorage) {
    ConfigStoreImpl config;
    config.setString("test_key", "test_value");
    std::string value = config.getString("test_key");
    EXPECT_EQ(value, "test_value");
}

// 测试基本向量存储和检索
TEST_F(ConfigStoreTest, VectorStorage) {
    ConfigStoreImpl config;
    std::vector<int> test_vec = {1, 2, 3, 4, 5};
    config.setVector("test_key", test_vec);
    std::vector<int> value = config.getVector("test_key");
    EXPECT_FALSE(test_vec.data() == value.data()) << "test_vec.data() == value.data()";
    EXPECT_EQ(value, test_vec);
}

// 测试不存在的键访问（整数）
TEST_F(ConfigStoreTest, NonexistentInt) {
    // 由于未初始化缓冲区的bug，预期此测试会失败
    ConfigStoreImpl config;
    try {
        int value = config.getInt("nonexistent");
        // 如果执行到这里，函数没有抛出异常，但我们无法验证其值
        // 因为它从未初始化的内存中读取
        FAIL() << "应该抛出异常或返回默认值";
    } catch (const std::exception& e) {
        // 修复后的预期行为是抛出异常或返回默认值
        SUCCEED();
    }
}

// 测试不存在的键访问（浮点数）
TEST_F(ConfigStoreTest, NonexistentFloat) {
    // 由于未初始化的default_value bug，预期此测试会失败
    ConfigStoreImpl config;
    try {
        float value = config.getFloat("nonexistent");
        // 如果执行到这里，函数没有抛出异常，但返回了未初始化的值
        FAIL() << "应该抛出异常或返回默认值";
    } catch (const std::exception& e) {
        // 修复后的预期行为是抛出异常或返回默认值
        SUCCEED();
    }
}

// 测试getInt中的类型不匹配
TEST_F(ConfigStoreTest, TypeMismatchInt) {
    ConfigStoreImpl config;
    config.setString("test_key", "not_an_int");
    try {
        int value = config.getInt("test_key");
        FAIL() << "应该抛出类型不匹配异常";
    } catch (const std::runtime_error& e) {
        EXPECT_STREQ(e.what(), "Type mismatch");
    }
}

// 测试buffer处理（边界内索引）
TEST_F(ConfigStoreTest, BufferProcessing) {
    ConfigStoreImpl config;
    // 使用边界内的有效索引应该成功执行
    bool result = true;
    try {
        config.processBuffer(5, 42); // 对于默认缓冲区大小（10），应该在边界内
    } catch (...) {
        result = false;
    }
    EXPECT_TRUE(result) << "有效索引不应导致错误";
}

// 测试buffer处理（越界索引）
TEST_F(ConfigStoreTest, BufferProcessingOutOfBounds) {
    ConfigStoreImpl config;
    
    // 注意：在C++中，数组越界访问不会自动抛出异常，而是导致未定义行为
    // 我们需要测试ConfigStore是否实现了边界检查
    
    // 方法1：如果实现了边界检查并抛出异常
    try {
        config.processBuffer(15, 42); // 对于默认缓冲区大小（10），越界
        
        // 如果没有抛出异常，则需要检查数组访问是否有边界检查的其他迹象
        // 例如，检查返回值、状态变量等
        
        // 由于我们知道原始实现没有上界检查，所以这里期望失败
        // 对于原始实现，这个测试可能无法正确验证，因为它会导致未定义行为
        FAIL() << "应该检测到越界并进行处理";
    } catch (const std::out_of_range& e) {
        // 如果实现添加了边界检查并抛出异常，这是期望的行为
        SUCCEED();
    } catch (...) {
        // 其他异常也可能表示边界检查
        SUCCEED();
    }
    
    // 方法2：检查是否有其他边界检查机制（如返回错误码）
    // 注意：这部分代码取决于修复后的实现方式，可能需要调整
}

// 测试set方法中的内存泄漏
TEST_F(ConfigStoreTest, MemoryLeakOnOverwrite) {
    // 此测试无法直接验证内存泄漏，但可以帮助使用Valgrind等工具进行手动验证
    ConfigStoreImpl config;
    config.setInt("test_key", 42);
    config.setInt("test_key", 43); // 覆盖应该清理旧值
    EXPECT_EQ(config.getInt("test_key"), 43);
}

// 测试sumBuffer方法
TEST_F(ConfigStoreTest, SumBuffer) {
    // 由于以下原因，预期此测试会失败：
    // 1. 未初始化的缓冲区值
    // 2. 循环中的越界错误
    
    // 注意：在C++中数组越界不会自动抛出异常
    ConfigStoreImpl config;
    
    // 方法1：如果实现添加了边界检查并抛出异常
    try {
        int sum = config.sumBuffer(0, 11);
        
        // 如果没有抛出异常，无法直接验证结果的正确性
        // 因为原始实现有未初始化内存访问和越界问题
        
        // 对于原始实现，这个测试可能不会产生可预测的结果
        FAIL() << "原始实现应该有边界检查或初始化问题";
    } catch (const std::exception& e) {
        // 如果实现添加了边界检查并抛出异常
        SUCCEED();
    } catch (...) {
        // 其他异常也可能表示边界检查
        SUCCEED();
    }
    
    // 方法2：验证返回值或其他状态指示边界检查
    // 这部分代码取决于修复后的实现方式
}