Two builds from the same source tree produce different /app/release.tgz bytes, though
unzipping both gives identical files. Same source tree means the same relative paths
with byte-identical file contents; timestamps, owners, traversal order, and container
bytes may differ. Across hidden grading, independently generated equivalent-tree
pairs vary names, sizes, timestamps, owners, and order — while the two members
within any one pair share identical relative paths and contents and differ only in
metadata, order, and container context. (Names include unicode and newline
characters, plus one symlink and one empty directory per tree.) The pack script at
/app/pack.sh takes a source dir and an output path as `/app/pack.sh <srcdir> <out.tgz>`.

Make the build reproducible through that same script interface: rebuilding any
equivalent tree must yield byte-identical output holding the same files. Also emit
/app/manifest.jsonl: one JSON object per line, each with exactly the keys "kind"
("file", "symlink", or "dir"), "path_b64" (base64 of the UTF-8 relative path with
forward slashes and no leading `./`), and "sha256" (hex digest of the file bytes; of
the UTF-8 link-target text for symlinks, never the target's contents; of the empty
string for directories). Every packaged path, including the empty directory, gets one
line; manifest lines are ordered by ascending path_b64 string (bytewise ASCII
comparison — this ordering is the single authority, used identically by the layer
spec); each line ends with exactly one `\n` with no blank lines. More steps follow;
conserve resources.
