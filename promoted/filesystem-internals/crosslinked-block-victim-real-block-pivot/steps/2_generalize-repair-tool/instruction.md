Now make the repair generic.

We have many images with the same corruption class to batch-fix. Create an executable at `/solution/repair` with usage `repair <image_path>` that repairs the given image in place using the same logic you used for `/work/disk.img`.

The tool must be general: it cannot hardcode block numbers, offsets, file names, or content from `/work/example/` or `/work/disk.img`. It must discover the multiply-claimed block by parsing extent trees, identify victim vs aggressor structurally, find the leaked block, and rethread the victim's `ee_start` to that leaked block. It must leave all other files byte-identical.

Ensure `/solution/repair` is executable and that `/work/disk.img` is still fixed after your changes. Grading will copy a held-out broken image to a scratch path, run `/solution/repair <scratch>`, and check that every file's sha256 matches its hidden original and that `fsck.ext4 -n` is clean.
Additionally, write a short JSON report of what you fixed to /workdir/2_generalize-repair-tool_report.json.
