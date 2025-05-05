#include <cmath>
#include "calendar_format.h"

// 检查是否为闰年
static bool isLeapYear(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

// 获取指定月份的天数
static int getDaysInMonth(int month, int year) {
    if (month == 2) {
        return isLeapYear(year) ? 29 : 28;
    } else if (month == 4 || month == 6 || month == 9 || month == 11) {
        return 30;
    } else { 
        // 1、3、5、7、8、10、12
        return 31;
    }
}

// 将时间戳转换为日期组件
static void timestampToDate(long timestampMs, int& year, int& month, int& day) {
    // 计算天数 (从1970-01-01开始)
    long days = timestampMs / (24 * 60 * 60 * 1000);
    
    // 计算年份
    year = 1970;
    while (true) {
        int daysInYear = isLeapYear(year) ? 366 : 365;
        if (days >= daysInYear) {
            days -= daysInYear;
            year++;
        } else {
            break;
        }
    }
    
    // 计算月份和日
    month = 1;
    int daysRemaining = days;
    
    for (; month <= 12; month++) {
        int daysInMonth = getDaysInMonth(month, year);
        
        if (daysRemaining >= daysInMonth) {
            daysRemaining -= daysInMonth;
        } else {
            day = daysRemaining + 1;
            break;
        }
    }
}

// 添加前导零
static std::string addLeadingZero(int number) {
    return (number < 10) ? "0" + std::to_string(number) : std::to_string(number);
}

std::string formatTimestamp(const std::string& format, long timestampMs) {
    int year, month, day;
    timestampToDate(timestampMs, year, month, day);
    
    // 构建结果字符串
    std::string result;
    size_t i = 0;
    
    while (i < format.length()) {
        char c = format[i];
        
        if (c == 'y') {
            result += std::to_string(year);
            // 跳过剩余的'y'字符
            while (i < format.length() && format[i] == 'y') i++;
        } else if (c == 'M') {
            result += addLeadingZero(month);
            // 跳过剩余的'M'字符
            while (i < format.length() && format[i] == 'M') i++;
        } else if (c == 'd') {
            result += addLeadingZero(day);
            // 跳过剩余的'd'字符
            while (i < format.length() && format[i] == 'd') i++;
        } else {
            result += c;
            i++;
        }
    }
    
    return result;
}