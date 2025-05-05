#include <gtest/gtest.h>
#include <iostream>
#include <cassert>
#include <string>

#include "../src/vector_invalid.h"

/**
 * Google Test测试套件，用于测试vector_invalid.cpp中的vector指针问题
 * 
 */
class VectorInvalidTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 在每个测试前设置
    }

    void TearDown() override {
        // 在每个测试后清理
    }
};

// 测试整数精度
TEST_F(VectorInvalidTest, Base) {
    int result = myFunc(22, 33);
    EXPECT_EQ(result, 33);
}