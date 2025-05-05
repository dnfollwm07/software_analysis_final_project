#include <gtest/gtest.h>
#include <iostream>
#include <cassert>
#include <string>
#include <memory>

#include "../src/dangling_pointer.h"

/**
 * Google Test测试套件，用于测试悬空指针问题
 * 
 * 这个测试套件旨在触发并检测代码中的悬空指针问题
 */

class DanglingPointerTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 在每个测试前设置
    }

    void TearDown() override {
        // 在每个测试后清理
    }
};

TEST_F(DanglingPointerTest, Basic) {
    auto ptr = createInt(100);
    
    EXPECT_EQ(*ptr, 100);
}

TEST_F(DanglingPointerTest, Overwrite) {
    auto dangerous_ptr = createInt(100);
    *dangerous_ptr = 200;
    EXPECT_EQ(*dangerous_ptr, 200);
}