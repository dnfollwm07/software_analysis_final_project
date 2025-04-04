# 软件分析期末项目

## 项目结构

```
project/
├── src/                  # 源代码目录
│   ├── static_analysis/  # 静态分析工具集成
│   ├── dynamic_analysis/ # 动态分析工具集成
│   ├── llm/              # LLM集成和提示词
│   ├── utils/            # 工具函数
│   └── sample_code.cpp   # 示例代码（包含需要分析的bug）
├── tests/                # 测试目录
│   └── test_sample_code.cpp # 示例代码测试
├── config/               # 配置文件目录
├── docs/                 # 文档目录
└── CMakeLists.txt        # CMake配置文件
```

## 构建与运行

### 构建要求

- CMake 3.10+
- C++14兼容的编译器
- Google Test（自动下载）

### 构建步骤

```bash
# 创建构建目录
mkdir build && cd build

# 配置项目
cmake ..

# 构建
cmake --build .

# 运行测试
ctest
```

## 测试框架

本项目使用 Google Test 作为测试框架。测试文件位于 `tests/` 目录中。

## 静态分析集成

本项目计划集成 Infer 等静态分析工具，用于检测以下类型的 bug：

- 空指针引用
- 内存泄漏
- 数组越界访问
- 未初始化变量

## 动态分析集成

本项目计划集成动态分析工具，用于：

- 测试用例生成
- 符号执行
- 覆盖率分析

## LLM 集成

本项目将整合 LLM 能力，用于：

- 代码分析
- Bug 修复建议
- 测试用例生成

## Features

The framework combines three key components:

1. **Static Analysis**: Uses tools like Infer to identify potential bugs in code
2. **Dynamic Analysis**: Generates test cases to validate code behavior
3. **LLM Integration**: Uses LLMs to suggest code repairs based on analysis results

## Getting Started

### Prerequisites

- Python 3.8+
- C++ compiler (for sample code)
- Infer static analyzer
- Valgrind (optional, for memory analysis)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure your LLM API key in `config/settings.json`

### Usage

1. Run static analysis on sample code:
   ```
   python -m src.static_analysis.run --target=src/sample_code.cpp
   ```

2. Generate and run tests:
   ```
   python -m src.dynamic_analysis.run --target=src/sample_code.cpp
   ```

3. Generate code repairs:
   ```
   python -m src.llm.repair --target=src/sample_code.cpp
   ```

## Example

The `src/sample_code.cpp` file contains a `ConfigStore` class with intentional bugs:
- Memory leaks
- Null pointer dereferences
- Array bounds violations
- Uninitialized variables

The framework:
1. Identifies these bugs using static analysis
2. Validates the issues using dynamic analysis/testing
3. Generates fixes using LLM suggestions

## License

This project is licensed under the MIT License - see the LICENSE file for details. 