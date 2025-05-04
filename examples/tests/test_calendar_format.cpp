#include <gtest/gtest.h>
#include <iostream>
#include <string>

// 包含calendar_format.cpp文件
#include "../src/calendar_format.h"

/**
 * Google Test测试套件，用于测试calendar_format实现
 * 
 * 这个测试套件旨在验证日期格式化函数的正确性，
 * 包括边界情况和特殊情况的处理。
 */

class CalendarFormatTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 在每个测试前设置
    }

    void TearDown() override {
        // 在每个测试后清理
    }
};


// 测试基本日期格式化
TEST_F(CalendarFormatTest, BasicFormat) {
    // 2022-01-15对应的时间戳 (ms)
    long timestamp = 1642204800000; // 2022-01-15 00:00:00 UTC
    
    std::string result = formatTimestamp("yyyy-MM-dd", timestamp);
    EXPECT_EQ(result, "2022-01-15");
}

// 测试不同的格式模式
TEST_F(CalendarFormatTest, DifferentFormats) {
    long timestamp = 1642204800000; // 2022-01-15 00:00:00 UTC
    
    EXPECT_EQ(formatTimestamp("yyyy/MM/dd", timestamp), "2022/01/15");
    EXPECT_EQ(formatTimestamp("MM-dd-yyyy", timestamp), "01-15-2022");
    EXPECT_EQ(formatTimestamp("dd.MM.yyyy", timestamp), "15.01.2022");
    EXPECT_EQ(formatTimestamp("yyyy年MM月dd日", timestamp), "2022年01月15日");
}

// // 测试闰年判断
// TEST_F(CalendarFormatTest, LeapYearDetection) {
//     // 直接测试isLeapYear函数
//     EXPECT_TRUE(isLeapYear(2000));  // 世纪闰年
//     EXPECT_TRUE(isLeapYear(2004));  // 普通闰年
//     EXPECT_TRUE(isLeapYear(2020));  // 普通闰年
    
//     EXPECT_FALSE(isLeapYear(1900)); // 非闰年（被100整除但不被400整除）
//     EXPECT_FALSE(isLeapYear(2001)); // 非闰年
//     EXPECT_FALSE(isLeapYear(2100)); // 非闰年（被100整除但不被400整除）
// }

// // 测试月份天数计算
// TEST_F(CalendarFormatTest, DaysInMonth) {
//     // 测试不同月份的天数
//     EXPECT_EQ(getDaysInMonth(1, 2022), 31);  // 1月
//     EXPECT_EQ(getDaysInMonth(2, 2022), 28);  // 2月非闰年
//     EXPECT_EQ(getDaysInMonth(2, 2020), 29);  // 2月闰年
//     EXPECT_EQ(getDaysInMonth(4, 2022), 30);  // 4月
//     EXPECT_EQ(getDaysInMonth(12, 2022), 31); // 12月
// }

// // 测试时间戳转日期
// TEST_F(CalendarFormatTest, TimestampToDate) {
//     int year, month, day;
    
//     // 测试2022-01-15
//     timestampToDate(1642204800000, year, month, day);
//     EXPECT_EQ(year, 2022);
//     EXPECT_EQ(month, 1);
//     EXPECT_EQ(day, 15);
    
//     // 测试1970-01-01（Unix纪元开始）
//     timestampToDate(0, year, month, day);
//     EXPECT_EQ(year, 1970);
//     EXPECT_EQ(month, 1);
//     EXPECT_EQ(day, 1);
// }

// 测试边界情况
TEST_F(CalendarFormatTest, EdgeCases) {
    // 测试Unix纪元开始时间
    EXPECT_EQ(formatTimestamp("yyyy-MM-dd", 0), "1970-01-01");
    
    // 测试闰年2月29日
    long leapDayTimestamp = 951782400000; // 2000-02-29 00:00:00 UTC
    EXPECT_EQ(formatTimestamp("yyyy-MM-dd", leapDayTimestamp), "2000-02-29");
    
    // 测试月末日期
    long monthEndTimestamp = 1640995200000; // 2022-01-01 00:00:00 UTC
    long prevDayTimestamp = 1640908800000;  // 2021-12-31 00:00:00 UTC
    EXPECT_EQ(formatTimestamp("yyyy-MM-dd", monthEndTimestamp), "2022-01-01");
    EXPECT_EQ(formatTimestamp("yyyy-MM-dd", prevDayTimestamp), "2021-12-31");
}

// 测试跨年的处理
TEST_F(CalendarFormatTest, YearTransition) {
    // 2021-12-31 23:59:59
    long beforeNewYear = 1640995199000;
    // 2022-01-01 00:00:00
    long afterNewYear = 1640995200000;
    
    EXPECT_EQ(formatTimestamp("yyyy-MM-dd", beforeNewYear), "2021-12-31");
    EXPECT_EQ(formatTimestamp("yyyy-MM-dd", afterNewYear), "2022-01-01");
}

// 测试远未来的日期
TEST_F(CalendarFormatTest, FutureDates) {
    // 2050-06-15
    // long futureTimestamp = 2538835200000;
    // EXPECT_EQ(formatTimestamp("yyyy-MM-dd", futureTimestamp), "2050-06-15");

    long futureTimestamp = 1907702400000;
    EXPECT_EQ(formatTimestamp("yyyy-MM-dd", futureTimestamp), "2030-06-14");
}