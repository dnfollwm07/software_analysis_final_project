#include <iostream>

void double_delete() {
    int* data = new int(10);
    delete data;
    delete data; // [INFER_WARNING] Releasing resource multiple times
}
