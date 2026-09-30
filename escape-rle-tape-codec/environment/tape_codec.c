#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int read_all(const char *path, unsigned char **buf, size_t *len) {
  FILE *f = fopen(path, "rb");
  if (!f || fseek(f, 0, SEEK_END) || (*len = (size_t)ftell(f), fseek(f, 0, SEEK_SET))) return 1;
  *buf = malloc(*len ? *len : 1);
  if (!*buf || fread(*buf, 1, *len, f) != *len) return 1;
  fclose(f);
  return 0;
}

static int encode(const unsigned char *in, size_t n) {
  unsigned char chk = 0;
  for (size_t i = 0; i < n;) {
    size_t j = i + 1;
    while (j < n && in[j] == in[i]) ++j;
    size_t span = j - i;
    if (span >= 4 && in[i] != 0xfe) {
      while (span) {
        unsigned char take = span > 127 ? 127 : (unsigned char)span;
        unsigned char token[4] = {chk, 0xfd, take, in[i]};
        if (fwrite(token, 1, 4, stdout) != 4) return 1;
        chk = 0;
        span -= take;
      }
    } else {
      for (size_t k = i; k < j; ++k) {
        if (in[k] == 0xfe && fputc(0xfe, stdout) == EOF) return 1;
        if (fputc(in[k], stdout) == EOF) return 1;
        chk ^= in[k];
      }
    }
    i = j;
  }
  return fputc(chk, stdout) == EOF;
}

static int decode(const unsigned char *in, size_t n) {
  size_t i = 0;
  while (i + 1 < n) {
    if (i + 3 < n && in[i + 1] == 0xfd && in[i + 2] > 0 && in[i + 2] <= 127) {
      for (unsigned int k = 0; k < in[i + 2]; ++k)
        if (fputc(in[i + 3], stdout) == EOF) return 1;
      i += 4;
    } else if (in[i] == 0xfe && i + 1 < n && in[i + 1] == 0xfe) {
      if (fputc(0xfe, stdout) == EOF) return 1;
      i += 2;
    } else {
      if (fputc(in[i], stdout) == EOF) return 1;
      ++i;
    }
  }
  return 0;
}

int main(int argc, char **argv) {
  if (argc != 2) {
    fprintf(stderr, "usage: %s <file>\n", argv[0]);
    return 2;
  }
  unsigned char *buf = NULL;
  size_t len = 0;
  if (read_all(argv[1], &buf, &len)) {
    fprintf(stderr, "read failed: %s\n", strerror(errno));
    return 1;
  }
  const char *base = strrchr(argv[0], '/');
  base = base ? base + 1 : argv[0];
  int rc = strstr(base, "decode") ? decode(buf, len) : encode(buf, len);
  free(buf);
  return rc;
}
