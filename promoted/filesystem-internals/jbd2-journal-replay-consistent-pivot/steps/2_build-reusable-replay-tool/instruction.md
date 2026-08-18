Your previous recovery to /app/recovered.img passed fsck. Now make it reusable.

Other machines will hit similar crashes with different images and logs, so we need a general program that can replay any detached jbd2 journal onto any crash image using the same logic you just used.

Build an executable at /app/replay with usage `/app/replay <disk_image> <journal_file> <output_image>`: it reads a crash image and its detached journal, writes the correctly recovered image to the third argument path. It must work on the shipped pair and on other pairs with the same layout.

For this step, running `/app/replay /app/disk.img /app/journal.bin /tmp/out.img` must produce an image that is fsck clean (`fsck.ext4 -n /tmp/out.img` exit 0) and byte-identical to your /app/recovered.img from step 1. The grader will also run it on that exact shipped sample and compare byte-for-byte against the true ground truth.

Do not yet create /app/fix_report.txt — that belongs to the next pivot. Keep the binary at /app/replay, keep /app/recovered.img valid, and rely on the parsing you already did for s_start, s_sequence and tag handling without re-deriving everything from scratch.

Title keywords jbd2 journal replay should still describe your work.
