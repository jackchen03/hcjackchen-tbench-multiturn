#!/usr/bin/env python3
import os
import struct
import sys

MASK = 0xffffffff


def rol(value, shift):
    shift &= 31
    return ((value << shift) | (value >> ((32 - shift) & 31))) & MASK


def f(x, y, z): return z ^ (x & (y ^ z))
def g(x, y, z): return (x & y) | (x & z) | (y & z)
def h(x, y, z): return x ^ y ^ z


def half_md4(buf, words):
    a, b, c, d = buf
    def rnd(func, aa, bb, cc, dd, word, shift, add=0):
        return rol((aa + func(bb, cc, dd) + word + add) & MASK, shift)
    for i, s in zip(range(8), (3,7,11,19,3,7,11,19)):
        if i % 4 == 0: a = rnd(f,a,b,c,d,words[i],s)
        elif i % 4 == 1: d = rnd(f,d,a,b,c,words[i],s)
        elif i % 4 == 2: c = rnd(f,c,d,a,b,words[i],s)
        else: b = rnd(f,b,c,d,a,words[i],s)
    for i, s in zip((1,3,5,7,0,2,4,6), (3,5,9,13,3,5,9,13)):
        if i in (1,0): a = rnd(g,a,b,c,d,words[i],s,0x5a827999)
        elif i in (3,2): d = rnd(g,d,a,b,c,words[i],s,0x5a827999)
        elif i in (5,4): c = rnd(g,c,d,a,b,words[i],s,0x5a827999)
        else: b = rnd(g,b,c,d,a,words[i],s,0x5a827999)
    for index, (i, s) in enumerate(zip((3,7,2,6,1,5,0,4), (3,9,11,15,3,9,11,15))):
        if index % 4 == 0: a = rnd(h,a,b,c,d,words[i],s,0x6ed9eba1)
        elif index % 4 == 1: d = rnd(h,d,a,b,c,words[i],s,0x6ed9eba1)
        elif index % 4 == 2: c = rnd(h,c,d,a,b,words[i],s,0x6ed9eba1)
        else: b = rnd(h,b,c,d,a,words[i],s,0x6ed9eba1)
    return [(buf[0]+a)&MASK,(buf[1]+b)&MASK,(buf[2]+c)&MASK,(buf[3]+d)&MASK]


def words(data, signed):
    length = len(data); pad = length | (length << 8); pad |= pad << 16
    result=[]; value=pad
    for index, byte in enumerate(data[:32]):
        component = byte - 256 if signed and byte >= 128 else byte
        value = (component + (value << 8)) & MASK
        if index % 4 == 3:
            result.append(value); value=pad
    if len(result) < 8: result.append(value & MASK)
    while len(result) < 8: result.append(pad & MASK)
    return result[:8]


def pass_hash(seed, name, signed):
    state=list(struct.unpack('<4I',seed))
    state[0] ^= rol(len(name), state[0] & 31)
    remaining=name
    while remaining:
        state=half_md4(state,words(remaining,signed)); remaining=remaining[32:]
    if not name: state=half_md4(state,words(b'',signed))
    return state


def dirhash(seed, name):
    signed=pass_hash(seed,name,True); unsigned=pass_hash(seed,name,False)
    return signed[1], unsigned[2]


def main():
    seed=bytes.fromhex(sys.argv[1]); name=os.fsencode(sys.argv[2])
    major,minor=dirhash(seed,name)
    print(f'{major:08x} {minor:08x}')


if __name__=='__main__': main()
