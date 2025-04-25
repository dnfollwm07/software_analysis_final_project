# Test Suite for LLM-Assisted Code Repair Project

This directory contains test cases for validating the code repair functionality of the project.

## Test Files

- `test_configstore.cpp`: Tests for the `ConfigStore` class in `src/sample_code.cpp`

## Running Tests

To compile and run the ConfigStore test:

```bash
# Compile the test
g++ -std=c++11 test_configstore.cpp -o test_configstore

# Run the test
./test_configstore
```

## Test Structure

The tests are designed to validate both the original code with bugs and the repaired code after LLM-assisted fixes. 

- The original code has intentionally introduced bugs
- Most tests are expected to fail before repairs
- After successful code repair, all tests should pass

## Expected Bugs in Sample Code

The sample code contains various bugs that static and dynamic analysis tools should detect:

1. **Memory Leaks**
   - Missing proper cleanup in destructors
   - Missing cleanup when overwriting values
   - Missing cleanup in error cases

2. **Null Pointer Dereferences**
   - Accessing uninitialized pointers
   - Missing null checks before dereferencing

3. **Array Bounds Violations**
   - Off-by-one errors in loops
   - Missing bounds checks in buffer operations

4. **Uninitialized Variables**
   - Using uninitialized memory
   - Returning uninitialized values

## Integration with Analysis Tools

After running the tests, you can use static and dynamic analysis tools to detect the bugs:

For static analysis with Infer:
```bash
infer run -- g++ -std=c++11 ../src/sample_code.cpp -o sample_code
```

For dynamic analysis with Valgrind:
```bash
valgrind --leak-check=full ./test_configstore
``` 