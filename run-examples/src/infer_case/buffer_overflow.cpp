#include <iostream>

void write_buffer(int* arr, int size) {
    for (int i = 0; i <= size; i++) {  // [INFER_WARNING] Buffer Overflow: accesses out-of-bounds
        arr[i] = i;
    }
}
