cmake_minimum_required(VERSION 3.10)
project(software_analysis_final_project)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 主要源代码目录
add_subdirectory(examples/src)

# Google Test 设置
#include(FetchContent)
#FetchContent_Declare(
#  googletest
#  URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
#)
# 对于 Windows: 防止覆盖父项目的编译器/链接器设置
# set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
#FetchContent_MakeAvailable(googletest)

# 启用测试
# enable_testing()
include(CTest)

# 添加测试子目录
#add_subdirectory(examples/tests) 