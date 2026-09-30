#define _GNU_SOURCE
#include <errno.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char **argv) {
    const char *dir = "/opt/ref/bin";
    const char *shown = "/opt/ref/bin/slabcompact";
    const char *hidden = "/opt/ref/bin/.reference-hidden-during-grade";
    if (argc < 2) return 64;
    int moved = rename(shown, hidden) == 0;
    chmod(dir, 0700);
    chmod("/tests", 0700);
    pid_t pid = fork();
    if (pid < 0) return 65;
    if (pid == 0) {
        setenv("SLAB_GRADE", "1", 1);
        if (setgroups(0, NULL) != 0 || setgid(65534) != 0 || setuid(65534) != 0) _exit(126);
        execvp(argv[1], &argv[1]);
        _exit(errno == ENOENT ? 127 : 126);
    }
    int status = 0;
    waitpid(pid, &status, 0);
    if (moved) rename(hidden, shown);
    chmod(dir, 0755);
    chmod("/tests", 0755);
    if (WIFEXITED(status)) return WEXITSTATUS(status);
    return 128 + WTERMSIG(status);
}
