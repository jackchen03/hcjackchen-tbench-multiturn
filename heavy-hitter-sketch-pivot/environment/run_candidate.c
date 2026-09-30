#include <errno.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    if (geteuid() != 0) return 126;
    if (chmod("/tests", 0700) != 0) return 126;
    pid_t pid = fork();
    if (pid < 0) return 126;
    if (pid == 0) {
        if (setgroups(0, NULL) != 0 || setgid(65534) != 0 || setuid(65534) != 0) _exit(126);
        execvp(argv[1], &argv[1]);
        _exit(errno == ENOENT ? 127 : 126);
    }
    int status = 0;
    if (waitpid(pid, &status, 0) < 0) status = 126 << 8;
    chmod("/tests", 0755);
    if (WIFEXITED(status)) return WEXITSTATUS(status);
    return 128;
}
