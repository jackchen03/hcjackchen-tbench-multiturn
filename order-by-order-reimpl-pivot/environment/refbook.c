#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ORDERS 4096
#define MAX_PRICES 4096

typedef struct {
    long ref;
    char side;
    long price;
    long size;
    int active;
} Order;

static Order orders[MAX_ORDERS];
static int order_count = 0;

static int find_order(long ref) {
    for (int i = 0; i < order_count; ++i) {
        if (orders[i].active && orders[i].ref == ref) return i;
    }
    return -1;
}

static void add_order(long ref, char side, long price, long size) {
    if (order_count >= MAX_ORDERS) {
        fprintf(stderr, "too many orders\n");
        exit(2);
    }
    orders[order_count++] = (Order){ref, side, price, size, 1};
}

static int compare_desc(const void *left, const void *right) {
    long a = *(const long *)left;
    long b = *(const long *)right;
    return (a < b) - (a > b);
}

static int compare_asc(const void *left, const void *right) {
    long a = *(const long *)left;
    long b = *(const long *)right;
    return (a > b) - (a < b);
}

static void emit_side(char side) {
    long prices[MAX_PRICES];
    int price_count = 0;
    for (int i = 0; i < order_count; ++i) {
        if (!orders[i].active || orders[i].side != side) continue;
        int seen = 0;
        for (int j = 0; j < price_count; ++j) {
            if (prices[j] == orders[i].price) seen = 1;
        }
        if (!seen) prices[price_count++] = orders[i].price;
    }
    qsort(prices, price_count, sizeof(long), side == 'B' ? compare_desc : compare_asc);
    for (int p = 0; p < price_count; ++p) {
        printf("%c %ld:", side, prices[p]);
        for (int i = 0; i < order_count; ++i) {
            if (orders[i].active && orders[i].side == side && orders[i].price == prices[p]) {
                printf(" %ld:%ld", orders[i].ref, orders[i].size);
            }
        }
        putchar('\n');
    }
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: refbook <feed>\n");
        return 2;
    }
    FILE *feed = fopen(argv[1], "r");
    if (!feed) {
        perror("feed");
        return 2;
    }
    char line[256];
    while (fgets(line, sizeof(line), feed)) {
        char type = 0;
        long ref = 0, other = 0, price = 0, size = 0;
        char side = 0;
        if (sscanf(line, " %c", &type) != 1) continue;
        if (type == 'A' && sscanf(line, "A %ld %c %ld %ld", &ref, &side, &price, &size) == 4) {
            add_order(ref, side, price, size);
        } else if (type == 'E' && sscanf(line, "E %ld %ld", &ref, &size) == 2) {
            int index = find_order(ref);
            if (index >= 0) {
                orders[index].size -= size;
                if (orders[index].size < 0) orders[index].size = 0;
            }
        } else if (type == 'X' && sscanf(line, "X %ld %ld", &ref, &size) == 2) {
            int index = find_order(ref);
            if (index >= 0) {
                orders[index].size -= size;
                if (orders[index].size <= 0) orders[index].active = 0;
            }
        } else if (type == 'D' && sscanf(line, "D %ld", &ref) == 1) {
            int index = find_order(ref);
            if (index >= 0) orders[index].active = 0;
        } else if (type == 'U' && sscanf(line, "U %ld %ld %ld %ld", &ref, &other, &price, &size) == 4) {
            int index = find_order(ref);
            if (index >= 0) {
                if (price == orders[index].price && size < orders[index].size) {
                    orders[index].ref = other;
                    orders[index].size = size;
                } else {
                    side = orders[index].side;
                    orders[index].active = 0;
                    add_order(other, side, price, size);
                }
            }
        }
    }
    fclose(feed);
    emit_side('B');
    emit_side('S');
    return 0;
}
