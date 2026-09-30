./probe.sh --hello V3 returns ERR_VERSION from the installed build/configd even though the source tree targets the new protocol. The build inputs disagree with the binary: compare gcc -E -dM src/config.h against make -n and strings build/configd | grep PROTO to find every stale layer.

Rebuild from the repo so ./probe.sh --hello V3 returns HELLO_V3_OK without editing probe.sh. The old handshake must keep failing: ./probe.sh --hello V2 still returns ERR_VERSION.
