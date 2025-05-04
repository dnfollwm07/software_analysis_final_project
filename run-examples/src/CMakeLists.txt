# 添加源文件
set(SOURCES
    main.cpp
    # config_store.cpp
    config_store_bug.cpp
    infer_case/dangling_pointer.cpp
    infer_case/leak_memory.cpp
    infer_case/loop_leak.cpp
    infer_case/null_dereference.cpp
    infer_case/uninitialized_variable.cpp
    infer_case/uninitialized_variable.cpp
    config_store_bug.cpp
    infer_case/out_of_bounds.cpp
    infer_case/buffer_overflow.cpp
    infer_case/double_delete.cpp

    infer_case/maybe_null.cpp
    infer_case/type_confusion.cpp


)

# 创建静态库，而不是可执行文件
# 这样我们可以在测试中链接它
add_library(sample_code_lib STATIC ${SOURCES})

# 可选：创建可执行文件（如果需要独立运行）
add_executable(sample_code ${SOURCES})