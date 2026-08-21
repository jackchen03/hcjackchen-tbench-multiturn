# VFAT directory notes

Entries are 32 bytes. The attribute byte is at `0x0B`, NTRes at `0x0C`, and the LFN checksum at `0x0D`. LFN entries use attribute `0x0F`; their UTF-16 code units occupy the standard 5+6+2 fields. The reference intentionally differs from canonical FAT behavior.
