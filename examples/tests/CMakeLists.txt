# 添加测试源文件
set(TEST_SOURCES
    test_config_store.cpp
)

# 添加测试可执行文件
add_executable(test_sample_code ${TEST_SOURCES})

# 链接 Google Test 和项目库
target_link_libraries(test_sample_code
    GTest::gtest_main
    GTest::gmock
    sample_code_lib
)

# 配置测试
include(GoogleTest)
gtest_discover_tests(test_sample_code) 