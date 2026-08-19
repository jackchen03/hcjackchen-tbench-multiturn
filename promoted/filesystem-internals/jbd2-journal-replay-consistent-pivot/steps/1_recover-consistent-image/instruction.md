The machine crashed last week and an ext4 image is inconsistent. Running `fsck.ext4 -n /app/disk.img` reports errors — allocated-but-marked-free, directory entries pointing at zeroed inodes, wrong free counts. Before the crash the filesystem layer had written its last batch of changes into a detached jbd2 journal, but never checkpointed them back to the main image, so /app/disk.img is missing that batch.

That batch's complete record is in /app/journal.bin as a standalone log file. It is no longer attached to the image (the image's journal inode is zeroed and needs_recovery is clear), so fsck cannot auto replay it — you have to read it yourself.

A previous teammate tried a simple replayer that just wrote logged blocks back sequentially, but its output still fails fsck and file contents don't match.

Recover the image to a consistent state: parse the detached jbd2 journal and apply its committed contents onto the crash image so the result would pass a filesystem check. Write the recovered image to /app/recovered.img. The hidden grader will run `fsck.ext4 -n /app/recovered.img` and it must exit 0 clean for this step.


Keywords that must appear in your work: jbd2 journal replay consistent.