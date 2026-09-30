#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static int compare_candidate(const char *path) {
  FILE *a = fopen("/opt/ref/bin/tape_encode", "rb");
  FILE *b = fopen(path, "rb");
  if (!a || !b) return 0;
  struct stat sa, sb;
  if (fstat(fileno(a), &sa) || fstat(fileno(b), &sb)) return 0;
  if (sb.st_size < 4 || llabs((long long)sa.st_size - (long long)sb.st_size) > 4096) return 0;
  unsigned char ma[4], mb[4];
  if (fread(ma, 1, 4, a) != 4 || fread(mb, 1, 4, b) != 4) return 0;
  if (ma[0] != 0x7f || ma[1] != 'E' || ma[2] != 'L' || ma[3] != 'F' ||
      mb[0] != 0x7f || mb[1] != 'E' || mb[2] != 'L' || mb[3] != 'F') return 0;
  rewind(a); rewind(b);
  long long same = 0, seen = 0;
  int ca, cb;
  while ((ca = fgetc(a)) != EOF && (cb = fgetc(b)) != EOF) {
    ++seen;
    if (ca == cb) ++same;
  }
  fclose(a); fclose(b);
  return seen > 0 && same * 100 >= seen * 90;
}

int main(int argc, char **argv) {
  if (geteuid() != 0) return 2;
  if (argc == 3 && !strcmp(argv[1], "--check")) return compare_candidate(argv[2]) ? 10 : 0;
  if (argc != 1) return 2;
  if (chmod("/opt/ref", 0000) == 0 || errno == ENOENT) return 0;
  perror("chmod /opt/ref");
  return 1;
}
