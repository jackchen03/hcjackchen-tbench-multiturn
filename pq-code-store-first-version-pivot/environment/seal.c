#include <stdio.h>
int main(int argc, char **argv) {
    static const unsigned char key[] = "stage-two-pq-writer-5f07986c";
    if (argc != 3) return 2;
    FILE *in = fopen(argv[1], "rb"), *out = fopen(argv[2], "wb");
    if (!in || !out) return 3;
    int c; size_t i = 0;
    while ((c = fgetc(in)) != EOF) { fputc(((unsigned char)c) ^ key[i % (sizeof(key)-1)], out); i++; }
    fclose(in); fclose(out); return 0;
}
