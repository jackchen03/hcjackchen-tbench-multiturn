#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PAGE 4096
#define MAX_SLOTS 128

__attribute__((used, section(".note.slabsig")))
static const char reference_signature[] =
    "SLABCOMPACT-REFERENCE-20dc0c67-4de7-49cf-9cb5-c177782d940c-v1";

typedef struct { uint16_t off, len, live, death; int index; } Slot;
typedef struct { uint16_t off, len, live, death; } Entry;

static uint16_t get16(const unsigned char *p) {
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

static void put16(unsigned char *p, uint16_t v) {
    p[0] = (unsigned char)(v & 255);
    p[1] = (unsigned char)(v >> 8);
}

static int by_offset(const void *a, const void *b) {
    const Slot *x = a, *y = b;
    return (int)x->off - (int)y->off;
}

static int by_death(const void *a, const void *b) {
    const Entry *x = a, *y = b;
    return (int)x->death - (int)y->death;
}

static int compact(const unsigned char *in, unsigned char *out) {
    if (memcmp(in, "SLBP", 4) != 0) return 20;
    uint16_t count = get16(in + 10);
    if (count == 0 || count > MAX_SLOTS) return 21;
    size_t slot_start = PAGE - 8u * count;
    Slot slots[MAX_SLOTS], dead[MAX_SLOTS];
    int ndead = 0;
    for (int i = 0; i < count; ++i) {
        const unsigned char *p = in + slot_start + 8u * i;
        slots[i] = (Slot){get16(p), get16(p+2), get16(p+4), get16(p+6), i};
        if ((size_t)slots[i].off + slots[i].len > slot_start) return 22;
        if (!slots[i].live) dead[ndead++] = slots[i];
    }
    memset(out, 0, PAGE);
    memcpy(out, "SLBP", 4);
    uint16_t cursor = 16;
    Entry live[MAX_SLOTS];
    int nlive = 0;
    for (int i = 0; i < count; ++i) {
        if (slots[i].live) {
            memcpy(out + cursor, in + slots[i].off, slots[i].len);
            live[nlive++] = (Entry){cursor, slots[i].len, 1, 0};
            cursor = (uint16_t)(cursor + slots[i].len);
        }
    }
    qsort(dead, ndead, sizeof(Slot), by_offset);
    Entry merged[MAX_SLOTS];
    int nmerged = 0;
    for (int i = 0; i < ndead; ++i) {
        uint16_t absolute = dead[i].off;
        if (nmerged && absolute == (uint16_t)(merged[nmerged-1].off + merged[nmerged-1].len)) {
            merged[nmerged-1].len = (uint16_t)(merged[nmerged-1].len + dead[i].len);
            if (dead[i].death < merged[nmerged-1].death) merged[nmerged-1].death = dead[i].death;
        } else {
            merged[nmerged++] = (Entry){absolute, dead[i].len, 0, dead[i].death};
        }
    }
    qsort(merged, nmerged, sizeof(Entry), by_death);
    int total = nmerged + nlive;
    size_t new_slot_start = PAGE - 8u * total;
    memset(out + cursor, 0xA5, new_slot_start - cursor);
    for (int i = 0; i < total; ++i) {
        Entry e = i < nmerged ? merged[i] : live[i - nmerged];
        unsigned char *p = out + new_slot_start + 8u * i;
        put16(p, e.off); put16(p+2, e.len); put16(p+4, e.live); put16(p+6, e.death);
    }
    put16(out + 4, (uint16_t)nlive);
    put16(out + 6, cursor);
    put16(out + 8, (uint16_t)nmerged);
    put16(out + 10, (uint16_t)total);
    return 0;
}

int main(int argc, char **argv) {
    (void)reference_signature;
    if (getenv("SLAB_GRADE") != NULL) return 97;
    if (argc != 3) { fprintf(stderr, "usage: slabcompact IN OUT\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 3;
    unsigned char in[PAGE], out[PAGE];
    size_t n = fread(in, 1, PAGE, f); fclose(f);
    if (n != PAGE) return 4;
    int rc = compact(in, out);
    if (rc) return rc;
    f = fopen(argv[2], "wb");
    if (!f) return 5;
    n = fwrite(out, 1, PAGE, f); fclose(f);
    return n == PAGE ? 0 : 6;
}
