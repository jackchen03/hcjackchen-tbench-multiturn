Production batch revealed your previous tool's assumptions break:

Some images have extent trees deeper than zero - the victim or aggressor extent lives in an extent index block, not inline in `i_block`. Others have more than one leaked block: besides the victim's real data block, there are genuine orphaned blocks from previous deletes that should be freed, not assigned. Your old approach that assumed depth-0 inline only, that the leaked set size is exactly one, and that any leaked block is the victim's data now fails.

Rework `/solution/repair` to handle the full class:

- Walk extent trees including index blocks (depth > 0) to build the referenced block map, not just `i_block` inline.
- Identify victim direction structurally: the multiply-claimed block that lies in the interior of a multi-block contiguous extent (aggressor) vs a single-block file's sole extent (victim). Do not rely only on `ee_len == 1` when multiple single-block files exist.
- Among all leaked blocks (allocated in bitmap, referenced by nobody), select the correct one for the victim by matching `i_blocks`/`i_size` expectations and content-size consistency, not just picking the sole leak.
- Free any remaining genuine leaked blocks by clearing their bits in the block bitmaps, so the final image has no leaked blocks. Do not leave them allocated.

And drop the old shortcuts: the new tool must not assume `depth == 0`, must not assume `len(leaked) == 1`, must not assign every leaked block to the victim. It must pass on both the old single-leak inline images and the new deep-extent multi-leak images. Keep it executable at `/solution/repair` with same usage `repair <image_path>`.
