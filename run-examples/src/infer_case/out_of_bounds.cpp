void out_of_bounds(int i) {
    int arr[5] = {0};
    if (i >= 0) {
        arr[i] = 42; // i < 5 보장 없음
    }
}
