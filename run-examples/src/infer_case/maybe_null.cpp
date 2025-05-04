void maybe_null(bool flag) {
    int* ptr = nullptr;
    if (flag) {
        ptr = new int(42);
    }
    *ptr = 100; // flag == false일 때 null dereference
}
