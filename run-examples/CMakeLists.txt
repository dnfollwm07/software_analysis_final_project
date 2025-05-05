cmake_minimum_required(VERSION 3.10)
project(Examples LANGUAGES C CXX)

# 设置C++标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置C标准
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 启用测试
enable_testing()

# 查找Google Test包
find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

# 添加源文件目录
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)

# 收集所有源文件
file(GLOB SOURCES "src/*.cpp" "src/*.c")
file(GLOB TEST_SOURCES "tests/*.cpp")

# 创建主库
add_library(example_lib STATIC ${SOURCES})

# 创建测试可执行文件
add_executable(run_tests ${TEST_SOURCES})
target_link_libraries(run_tests example_lib ${GTEST_LIBRARIES} pthread)

# 添加测试
add_test(NAME run_tests COMMAND run_tests)

# 设置编译选项
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    # 为GCC和Clang设置警告标志
    target_compile_options(example_lib PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(run_tests PRIVATE -Wall -Wextra -Wpedantic)
endif()

# 为C++文件设置C++编译选项
set_source_files_properties(${SOURCES} PROPERTIES COMPILE_FLAGS "")
foreach(source ${SOURCES})
    get_filename_component(ext ${source} EXT)
    if(ext STREQUAL ".cpp")
        set_source_files_properties(${source} PROPERTIES COMPILE_FLAGS "-std=c++11")
    elseif(ext STREQUAL ".c")
        set_source_files_properties(${source} PROPERTIES COMPILE_FLAGS "-std=c99")
    endif()
endforeach()

# 输出信息
message(STATUS "C++ compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "C compiler: ${CMAKE_C_COMPILER}")
message(STATUS "C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "C standard: ${CMAKE_C_STANDARD}") 