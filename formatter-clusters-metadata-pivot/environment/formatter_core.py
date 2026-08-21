import os
import struct
import sys

BLOCK_SIZE = 1024
BLOCKS_PER_GROUP = 8192
INODES_PER_GROUP = 128
INODE_SIZE = 128
INODE_TABLE_BLOCKS = INODES_PER_GROUP * INODE_SIZE // BLOCK_SIZE


def align_up(value, stride):
    return ((value + stride - 1) // stride) * stride


def compute_layout(size_mib, stride, flex, include_modulo=True):
    if size_mib < 4 or stride < 1 or flex < 1:
        raise ValueError("size must be >=4 and stride/flex must be positive")
    total_blocks = size_mib * 1024
    groups = (total_blocks - 1 + BLOCKS_PER_GROUP - 1) // BLOCKS_PER_GROUP
    descriptors = [None] * groups
    used = {1, 2}
    pad_blocks = 0
    root_block = None
    for flex_start in range(0, groups, flex):
        flex_index = flex_start // flex
        count = min(flex, groups - flex_start)
        natural = max(3, 1 + flex_start * BLOCKS_PER_GROUP)
        block_bitmap_start = align_up(natural, stride)
        used.update(range(natural, block_bitmap_start))
        pad_blocks += block_bitmap_start - natural
        used.update(range(block_bitmap_start, block_bitmap_start + count))
        inode_bitmap_natural = block_bitmap_start + count
        inode_bitmap_start = align_up(inode_bitmap_natural, stride)
        used.update(range(inode_bitmap_natural, inode_bitmap_start))
        pad_blocks += inode_bitmap_start - inode_bitmap_natural
        used.update(range(inode_bitmap_start, inode_bitmap_start + count))
        inode_table_natural = inode_bitmap_start + count
        inode_table_start = align_up(inode_table_natural, stride)
        if include_modulo:
            inode_table_start += flex_index % stride
        used.update(range(inode_table_natural, inode_table_start))
        pad_blocks += inode_table_start - inode_table_natural
        used.update(range(inode_table_start, inode_table_start + count * INODE_TABLE_BLOCKS))
        for offset in range(count):
            group = flex_start + offset
            descriptors[group] = (
                block_bitmap_start + offset,
                inode_bitmap_start + offset,
                inode_table_start + offset * INODE_TABLE_BLOCKS,
            )
        if flex_start == 0:
            root_block = inode_table_start + count * INODE_TABLE_BLOCKS
            used.add(root_block)
    return total_blocks, groups, descriptors, used, root_block, pad_blocks


def group_bounds(group, total_blocks):
    start = 1 + group * BLOCKS_PER_GROUP
    return start, min(start + BLOCKS_PER_GROUP, total_blocks)


def pack_superblock(groups, total_blocks, free_blocks):
    data = bytearray(BLOCK_SIZE)
    values = {
        0: groups * INODES_PER_GROUP, 4: total_blocks, 8: 0, 12: free_blocks,
        16: groups * INODES_PER_GROUP - 10, 20: 1, 24: 0, 28: 0,
        32: BLOCKS_PER_GROUP, 36: BLOCKS_PER_GROUP, 40: INODES_PER_GROUP,
        44: 0, 48: 0, 64: 0, 68: 0, 72: 0, 76: 1, 84: 11,
        92: 0, 96: 0x202, 100: 0,
    }
    for offset, value in values.items():
        struct.pack_into("<I", data, offset, value)
    for offset, value in ((52, 0), (54, 0xFFFF), (56, 0xEF53), (58, 1),
                          (60, 1), (62, 0), (80, 0), (82, 0),
                          (88, INODE_SIZE), (90, 0)):
        struct.pack_into("<H", data, offset, value)
    data[120:136] = b"MYFS-FLEX".ljust(16, b"\0")
    return data


def write_image(output_path, size_mib, stride, flex, include_modulo=True):
    total, groups, descriptors, used, root_block, pad_blocks = compute_layout(
        size_mib, stride, flex, include_modulo
    )
    free_by_group = []
    for group in range(groups):
        start, end = group_bounds(group, total)
        free_by_group.append((end - start) - sum(start <= block < end for block in used))
    with open(output_path, "wb") as image:
        image.truncate(total * BLOCK_SIZE)
        image.seek(BLOCK_SIZE)
        image.write(pack_superblock(groups, total, sum(free_by_group)))
        image.seek(2 * BLOCK_SIZE)
        for group, (block_bitmap, inode_bitmap, inode_table) in enumerate(descriptors):
            gd = bytearray(32)
            struct.pack_into("<IIIHHH", gd, 0, block_bitmap, inode_bitmap, inode_table,
                             free_by_group[group], INODES_PER_GROUP - (10 if group == 0 else 0),
                             1 if group == 0 else 0)
            image.write(gd)
        for group, (block_bitmap, inode_bitmap, _) in enumerate(descriptors):
            start, end = group_bounds(group, total)
            bitmap = bytearray(BLOCK_SIZE)
            for block in used:
                if start <= block < end:
                    bit = block - start
                    bitmap[bit // 8] |= 1 << (bit % 8)
            for bit in range(end - start, BLOCKS_PER_GROUP):
                bitmap[bit // 8] |= 1 << (bit % 8)
            image.seek(block_bitmap * BLOCK_SIZE)
            image.write(bitmap)
            inode_bits = bytearray(BLOCK_SIZE)
            if group == 0:
                for bit in range(10):
                    inode_bits[bit // 8] |= 1 << (bit % 8)
            image.seek(inode_bitmap * BLOCK_SIZE)
            image.write(inode_bits)
        inode = bytearray(INODE_SIZE)
        struct.pack_into("<H", inode, 0, 0x41ED)
        struct.pack_into("<I", inode, 4, BLOCK_SIZE)
        struct.pack_into("<H", inode, 26, 2)
        struct.pack_into("<I", inode, 28, 2)
        struct.pack_into("<I", inode, 40, root_block)
        image.seek(descriptors[0][2] * BLOCK_SIZE + INODE_SIZE)
        image.write(inode)
        directory = bytearray(BLOCK_SIZE)
        struct.pack_into("<IHBb", directory, 0, 2, 12, 1, 2)
        directory[8:9] = b"."
        struct.pack_into("<IHBb", directory, 12, 2, BLOCK_SIZE - 12, 2, 2)
        directory[20:22] = b".."
        image.seek(root_block * BLOCK_SIZE)
        image.write(directory)
    os.utime(output_path, (0, 0))
    return pad_blocks


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("usage: myfs-mkfs <output.img> <size MiB> <stride> <flex>")
    write_image(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), True)
