# 添加源文件
set(SOURCES
    sample_code.cpp
)

# 创建静态库，而不是可执行文件
# 这样我们可以在测试中链接它
add_library(sample_code_lib STATIC ${SOURCES})

# 可选：创建可执行文件（如果需要独立运行）
add_executable(sample_code ${SOURCES})