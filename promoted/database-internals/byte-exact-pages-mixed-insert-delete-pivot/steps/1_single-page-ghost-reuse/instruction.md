We have a legacy primary key index tool that maintains a B+ tree index file on disk from a stream of insert/delete operations. The file is a compact binary made of 256-byte pages with a slot directory. The colleagues who defined the disk format and maintenance logic left no docs, only a stripped binary.

Your current rewrite matches the old tool on insert-only streams, but as soon as deletes appear the bytes diverge — even though logical key sets are identical. The difference is only visible by hexdumping raw pages, not via the logical dump. It shows up especially when space is repeatedly freed and reused after deletes.

The old tool is still in the environment at `/verifier/btapply` usable as `/verifier/btapply <output file>` reading operations from stdin, each line `I <key>` for insert or `D <key>` for delete (keys are printable strings without spaces). `/verifier/dump-tree <index file>` prints keys in logical order. `/app/samples/` has a few small example streams and their old-tool outputs for warmup — those small samples are guaranteed to fit within a single page and never trigger splits or merges.

Focus on the single-page case first. For streams that stay within one page, figure out exactly how this engine handles deletes at the page level and how later inserts reuse freed space — the slot directory, cell bytes, counters and high-water mark must all become byte-identical.

Deliver an executable at `/app/btapply` with identical usage `/app/btapply <output file>` reading `I <key>` / `D <key>` lines from stdin and writing the whole index file. For this step we will validate it only on single-page streams (delete-heavy, delete-then-reinsert on the same page) with disjoint keys from the samples. All files must be byte-exact vs the old tool on those streams. More steps will follow, so conserve the binary and its conventions.

Do not write `/app/split_boundary.json` or `/app/migration_report.json` yet.
