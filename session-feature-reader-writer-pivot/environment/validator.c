#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t read_u32(const unsigned char *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint32_t crc32_bytes(const unsigned char *data, size_t length) {
    uint32_t crc = 0xffffffffu;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; bit++)
            crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return crc ^ 0xffffffffu;
}

static int consume_varint(const unsigned char *data, size_t limit, size_t *offset) {
    for (int count = 0; count < 10; count++) {
        if (*offset >= limit) return 0;
        if ((data[(*offset)++] & 0x80u) == 0) return 1;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    FILE *file = fopen(argv[1], "rb");
    if (!file) return 2;
    if (fseek(file, 0, SEEK_END) != 0) return 2;
    long size_long = ftell(file);
    if (size_long < 64 || size_long % 64 != 0) return 1;
    rewind(file);
    size_t size = (size_t)size_long;
    unsigned char *data = malloc(size);
    if (!data || fread(data, 1, size, file) != size) return 2;
    fclose(file);
    if (memcmp(data, "SFS1", 4) != 0) return 1;
    uint32_t count = read_u32(data + 4);
    size_t offset = 8;
    size_t limit = size - 4;
    for (uint32_t session = 0; session < count; session++) {
        if (offset + 9 > limit) return 1;
        uint8_t events = data[offset + 4];
        offset += 9;
        for (uint8_t i = 0; i < events; i++)
            if (!consume_varint(data, limit, &offset)) return 1;
        for (uint8_t i = 0; i < events; i++) {
            if (offset >= limit) return 1;
            unsigned char first = data[offset++];
            if ((first & 0x10u) && !consume_varint(data, limit, &offset)) return 1;
        }
    }
    if (offset + 2 > limit || data[offset] != 0xff || data[offset + 1] != 0xff) return 1;
    size_t records_end = offset + 2;
    for (size_t i = records_end; i < limit; i++)
        if (data[i] != 0) return 1;
    uint32_t stored = read_u32(data + limit);
    uint32_t computed = crc32_bytes(data, records_end);
    free(data);
    return stored == computed ? 0 : 1;
}
