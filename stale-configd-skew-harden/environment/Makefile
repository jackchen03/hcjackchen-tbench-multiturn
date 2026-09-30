CC=gcc
CFLAGS=-O2 -Wall -DPROTOCOL_V2
build/configd: src/configd.c src/config.h
	mkdir -p build
	$(CC) $(CFLAGS) -Isrc -o $@ src/configd.c
