A storage appliance writes an ext4 image where large directories use htree indexing. The image is supposed to use half_md4 dirhash, but running `fsck.ext4 -n` on a regular Linux host reports every htree-indexed directory as having mismatched index hashes. There is a reference oracle binary in the container at `/usr/local/bin/dirhash-oracle` (firmware's hash implementation) you can probe with arbitrary seeds and filenames to observe correct behavior. It will not be present in the final evaluation environment.

Build a standalone tool that reproduces the firmware's directory hash for ASCII-only filenames.

Create an executable at `/usr/local/bin/dirhash` invoked as `dirhash <seed_hex> <filename>`: first argument is 32 hex lowercase chars (16-byte hash_seed), second is a filename (for this step tests use only pure-ASCII names). It must print one line to stdout with two space-separated values, major hash first then minor hash, each as 8 lower-case hex digits padded with leading zeros, no `0x` prefix, then exit 0.

The sample ext4 image at `/work/appliance.img` was built with `mke2fs -O dir_index` and contains a directory whose `dx_root` hash_version field claims `EXT2_HASH_HALF_MD4`. The sample seed used in documentation is different from hidden seeds.
