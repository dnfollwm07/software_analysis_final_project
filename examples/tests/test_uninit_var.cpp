#include <gtest/gtest.h>
#include <iostream>
#include <cassert>
#include <string>
#include <vector>
#include <memory>

#include "../src/uninit_var.h"

/**
 * Google Test测试套件，用于测试未初始化变量问题
 * 
 * 这个测试套件旨在触发并检测未初始化变量带来的问题
 */

class UninitVarTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 在每个测试前设置
    }

    void TearDown() override {
        // 在每个测试后清理
    }
};

// 测试正常情况下的计算（正数输入）
TEST_F(UninitVarTest, PositiveInput) {
    int result = myCalculate(101);
    EXPECT_EQ(result, 208);
}

// 测试未初始化变量问题（负数输入）
TEST_F(UninitVarTest, NegativeInput) {
    int result = myCalculate(-5);
    EXPECT_EQ(result, -9);
}