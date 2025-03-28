# LLM-Assisted Code Repair Framework

這個項目實現了一個自動化代碼修復框架，結合了靜態分析、動態測試和大型語言模型（LLM）來修復C++代碼中的錯誤。

## 項目結構

- `src/correct_code.cpp`: 無錯誤的參考實現
- `src/test_code.cpp`: 包含多種錯誤的測試代碼
- `tests/test_configstore.cpp`: 測試用例
- `code_repair.py`: 主要的代碼修復腳本

## 工作流程

1. 運行測試以確認代碼是否有錯誤
2. 使用靜態分析（如Infer）識別潛在問題
3. 將代碼、測試結果和分析結果發送給LLM
4. LLM生成修復建議
5. 重新測試修復後的代碼

## 框架設計說明

本框架的設計理念是將靜態分析、動態測試和大語言模型結合起來，形成一個完整的代碼修復流程：

### 靜態分析部分
- 使用 Infer 檢測常見的內存錯誤、空指針解引用等問題
- 如未安裝 Infer，則退化為使用編譯器警告
- 分析結果會格式化後作為 LLM 的輸入

### 動態測試部分
- 設計了一套完整的測試框架，分別測試正確和錯誤的代碼
- 測試不僅用於檢測錯誤，也用於驗證修復的效果
- 測試結果會格式化後作為 LLM 的輸入

### LLM 部分
- 提供了完整的 prompt 工程，幫助 LLM 理解問題並生成有效的修復
- 支持通過 API 調用真實的 LLM 服務
- 提供了本地簡單修復功能作為演示

### 完整流程
1. 首先確保正確的參考代碼能通過所有測試
2. 對包含錯誤的代碼運行測試，收集測試結果
3. 對包含錯誤的代碼進行靜態分析，收集分析結果
4. 將代碼、測試結果和分析結果組合為 prompt 發送給 LLM
5. LLM 生成修復後的代碼
6. 對修復後的代碼再次運行測試，驗證修復效果

## 安裝依賴

```bash
# 安裝Python依賴
pip install openai

# 可選：安裝Infer靜態分析工具
# 請參考: https://fbinfer.com/docs/getting-started/
```

## 使用方法

### 測試基準代碼

首先確認正確的代碼能通過所有測試：

```bash
# 編譯和運行基準測試
g++ -std=c++11 -DTEST_CORRECT tests/test_configstore.cpp -o tests/bin/test_configstore
./tests/bin/test_configstore
```

### 運行測試以檢測錯誤

測試含有錯誤的代碼：

```bash
# 編譯和運行測試
g++ -std=c++11 tests/test_configstore.cpp -o tests/bin/test_configstore
./tests/bin/test_configstore
```

### 運行靜態分析

使用編譯器警告進行靜態分析：

```bash
g++ -Wall -Wextra -Werror -std=c++11 src/test_code.cpp -o src/test_code -DTESTING
```

如果安裝了 Infer，可以使用：

```bash
infer run --enable-issue-type NULL_DEREFERENCE,MEMORY_LEAK,BUFFER_OVERRUN,UNINITIALIZED_VALUE -- g++ -std=c++11 src/test_code.cpp -c
```

### 運行修復腳本

使用Python腳本修復有錯誤的代碼：

```bash
# 基本用法
python code_repair.py --code src/test_code.cpp --test tests/test_configstore.cpp

# 使用OpenAI API（需要API密鑰）
python code_repair.py --code src/test_code.cpp --test tests/test_configstore.cpp --api-key YOUR_API_KEY

# 跳過Infer分析
python code_repair.py --code src/test_code.cpp --test tests/test_configstore.cpp --skip-infer

# 指定輸出文件
python code_repair.py --code src/test_code.cpp --test tests/test_configstore.cpp --output fixed_code.cpp

# 完整選項
python code_repair.py --code src/test_code.cpp --test tests/test_configstore.cpp --correct src/correct_code.cpp --output src/test_code_fixed.cpp --api-key YOUR_API_KEY --debug
```

## 命令行選項

- `--code`: 包含錯誤的代碼文件路徑（必需）
- `--test`: 測試文件路徑（必需）
- `--correct`: 正確實現的文件路徑（可選，用於驗證）
- `--output`: 修復後代碼的保存路徑（可選）
- `--api-key`: LLM服務的API密鑰（可選）
- `--skip-infer`: 跳過Infer靜態分析（可選）
- `--debug`: 啟用詳細調試輸出（可選）

## 示例錯誤

測試代碼中包含以下幾類常見錯誤：

1. **內存洩漏**：
   - 析構函數中缺少適當的清理
   - 當覆蓋現有值時沒有清理舊值

2. **空指針解引用**：
   - 使用未初始化的指針
   - 缺少空指針檢查

3. **數組邊界錯誤**：
   - 循環中的越界錯誤
   - 缺少上界檢查

4. **未初始化變量**：
   - 使用未初始化的內存
   - 返回未初始化的值

## 配置文件和測試文件的設計

### 配置文件說明
- `src/correct_code.cpp`: 包含了一個完全正確的 `ConfigStore` 類實現，沒有任何內存安全問題
- `src/test_code.cpp`: 包含有意設計的錯誤，用於測試代碼修復框架的效果

### 測試文件說明
- `tests/test_configstore.cpp`: 包含一系列測試用例，設計來檢測 `ConfigStore` 類中的各種錯誤
- 通過使用 `TEST_CORRECT` 宏可以在測試正確和錯誤的代碼之間切換
- 測試結果會提供關於哪些功能通過和失敗的信息，幫助 LLM 進行診斷

## 擴展框架

以下是一些可能的擴展方向：

1. **支持更多語言**: 擴展框架支持 Python、Java 等其他語言
2. **集成更多分析工具**: 添加 Valgrind、AddressSanitizer 等工具的支持
3. **優化提示工程**: 改進 LLM 提示模板，提高修復質量
4. **添加修復歷史**: 記錄修復嘗試，允許回滾到之前的版本
5. **自動化測試生成**: 根據代碼結構自動生成測試用例

## 額外說明

- 如果沒有安裝Infer，代碼將回退到使用編譯器警告
- 如果沒有OpenAI API密鑰，腳本將使用內置的簡單修復作為示範
- 生成的修復代碼將保存為原文件名加上"_fixed"後綴

## License

This project is licensed under the MIT License - see the LICENSE file for details. 