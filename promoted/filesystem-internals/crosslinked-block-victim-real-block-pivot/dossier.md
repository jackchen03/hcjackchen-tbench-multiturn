# Dossier — crosslinked-block-victim-real-block-pivot

Canary GUID: TBENCH-MT-FSINT-XLINK-24-ac3c809e-ad1b-475d-a562-0488d8299043
Original single-turn: cross-linked-block-where-the-victim-s-real-block-24 (TBENCH-FSINT-XLINK-24-3401be01-0628-4ce6-be43-98cb0b5de30c)

## One-line litmus (task + per-step)

**Task overall:** A senior ext4 engineer who knows on-disk format cold still produces WRONG output in one pass because the textbook `e2fsck -fy` clone-and-free yields a consistent but byte-wrong image, and fusing cross-link + leak to rethread victim to leaked block requires probing extent trees + block bitmaps.

**Step1 diagnose-and-repair-disk:** A senior engineer reading `/work/disk.img` sees `ls`/`cat` healthy and runs `e2fsck -fy` which reports fixing multiply-claimed + leaked — still WRONG because it clones aggressor bytes into victim and frees real data. Correct requires manually locating victim vs aggressor interior-of-run and leaked block and byte-patching `ee_start` without mount.

**Step2 generalize-repair-tool:** A senior engineer who fixed `disk.img` by hand with hardcoded offsets still fails because held-out images have disjoint layout/block numbers/file names — tool must parse extent trees generically, build refcount map, find duplicate, identify victim structurally, locate leak via bitmap vs refset. Hardcoded offsets RED.

**Step3 handle-deep-extents-and-selective-leaks:** A senior engineer whose step2 tool assumed inline depth-0 extents and single leaked block == victim data now fails: some images have depth>0 index blocks and multiple leaked blocks where only one is victim's real data, others must be freed. Old heuristic assigning sole leak to len-1 victim and leaving bitmap untouched yields WRONG content or fsck not clean. Requires full tree walk + selective leak matching + freeing genuine leaks, dropping old shortcuts.

## Mechanism chain (load-bearing, not story)

Coupled duplicate-block (cross-link) + leaked-block where leak IS victim's original data + victim direction via interior-of-contiguous-run geometry → single field `ee_start` rethread restores victim and simultaneously resolves both fsck errors without bitmap edit. Extension to generic tool adds layout-general extent parsing + bitmap-vs-refset leak enumeration + structural victim identification. Pivot adds depth>0 extent index traversal + multi-leak disambiguation (size/blocks coherence) + bitmap clearing for genuine orphans. Mechanism dedup vs other FS tasks: dirent-inode-number clobber tasks use link-count+file_type, not block sharing; byte-exact reconstruction tasks use unwritten extents + manifest, not cross-link+leak coupling; journal/FAT tasks unrelated. Core distinct insight: leak is not janitorial, it is data to be rethreaded, and selective free vs assign must be decided.

## Per-step diagnosis / design

**Step1:** Parse superblock at 1024 (block size = 1024 << log_block_size), group descriptors, inode tables. For each inode with `EXT4_EXTENTS_FL (0x80000)`, parse inline extent header magic `0xF30A` depth 0 entries -> list `(ee_block, ee_len, ee_start, offset_in_i_block)`. Build `ref: phys->[(ino, off, len, start)]`. Find block with `len(owners)>1` = D. Owners: aggressor has `el>=4` contiguous run covering D in interior `0<k<L-1`, victim has `el==1`. Find leaked: for each group, read block bitmap block `bg_block_bitmap_lo`, check bits allocated but not in `ref`. Expect 1 leaked P_B originally. Patch victim inode's `ee_start_lo/hi` at `inode_off+40+o+8/+6` from D to P_B via `r+b` byte patch. Verify `debugfs cat` now returns original, `fsck -n` clean.

**Step2:** Same logic but must work for any image: do not hardcode group count offsets, must support any block size (4096 pinned but code generic), any inode size, any victim/aggressor file names. Build reference tool `/solution/repair <path>` in python: parse sb, gdt, walk all inodes, build ref map, find dup, identify victim by `(len==1 and D interior of other owner's run)` + i_blocks single-block match, find leaked set via bitmap scan, assert at least 1, rethread victim to matching leaked. Make executable chmod +x.

**Step3:** Extend walker to depth>0: if extent header depth>0, read index entries `(ei_block, ei_leaf_lo/hi)`, recursively read leaf/index blocks to collect all extents. Now dup detection works even when victim/aggressor extents live in leaf blocks. Multi-leak: bitmap scan may return >1 leaked blocks. Need disambiguation: candidate leaked blocks are those where block's content size matches victim's `i_size` expectation and victim's `i_blocks` would be satisfied by that block count (single). For genuine orphans (previous deletes), no inode needs them; after rethread, any leaked still unreferenced must have its bitmap bit cleared. So steps: after rethread, rebuild ref, remaining leaked -> clear bits in respective bitmap blocks (read-modify-write). This pivots away from step2's invariant "bitmap needs no edit" which only held for single-leak case. Also must drop assumption depth==0 and leak count==1.

## Why discriminates — plausible strong attempts RED per step

**Step1 attempts:**
- A1: Run `e2fsck -fy /work/disk.img`. Pass 1B clones D copying aggressor bytes to new block for victim, pass 5 frees P_B. Image fsck clean but victim sha256 == aggressor block-k, not original → RED content.
- A2: Manual clone same as e2fsck: detect dup, allocate new free block, memcpy D bytes, point victim there, clear P_B bitmap. Same WRONG bytes as A1, real data lost → RED.
- A3: Right idea leak = data but wrong direction: rethread aggressor's interior slot to P_B, leaving victim aliased + aggressor corrupted (logical block k now B's bytes) → both files wrong, fsck may be clean but content RED.
- A4: Hardcode sample offsets from `/work/example/broken.img` (e.g., inode table at block X, patch at byte Y) to fix `/work/disk.img` — fails because layouts differ → either no effect or corrupts wrong inode → RED.

**Step2 attempts:**
- B1: Hardcode step1's P_B/D/ino offsets discovered for `/work/disk.img` inside `/solution/repair`. Passes on disk.img but fails on held-out where layout/content disjoint → victim still wrong on held-out → RED held-out sha mismatch.
- B2: Fix dup by always giving victim a fresh block cloned from D (e2fsck logic) inside generic tool — consistent but wrong on all images, content RED (same as A1).
- B3: Identify victim solely by `ee_len==1` without interior-run check, picks wrong single-block file when multiple single-block files exist (holds for step3 variant but also breaks generic). In images with two single-block files, may rethread healthy file → both wrong.

**Step3 attempts:**
- C1: Keep depth-0-only parser from step2 — fails to find extents that live in index blocks, so ref map misses dup or leak, no repair or wrong repair, fsck still reports multiply-claimed → RED.
- C2: Assume single leaked block == victim's data, when multiple leaks exist picks first leaked arbitrarily (e.g., smallest block number) which may be genuine orphan, not victim's data → victim gets garbage orphan bytes, real leaked data later freed or left leaked → content RED + fsck leak RED.
- C3: Assign every leaked block to victim (does not free genuine leaks) or freeds all leaks including victim's real data — first leaves fsck not clean (still leaked or victim still wrong), second destroys victim data → RED.
- C4: Still relies on len==1 heuristic without interior-contiguous geometry, picks healthy single-block file as victim when multiple single-block files — corrupts healthy file.

**Cross-step failures:**
- Loses context: step2 tool rewrites `/work/disk.img` from scratch ignoring step1 fix, or step3 tool drops executable bit or changes CLI to different args, breaking `repair <path>` contract → RED step2 regression.
- Over-execution: step1 script already creates `/solution/repair` that hardcodes depth-0 logic (doing step2+3 early). Then step3 requires absence of old shortcuts but over-exec tool already bakes them and fails multi-leak test because it was built before learning multi-leak requirement. Grader's over-exec negatives check that step1 did not create file `/solution/repair` containing string `depth`? Actually we guard via identifiers from later steps — if step1 creates `/solution/repair` it trips over-exec negative for step1.
- Wrong data flow: step3 parser walks extent tree but starves buffer (does not re-read updated bitmap after patch) so freed genuine leaks still show allocated → fsck not clean.

## Recall resistance per step + cross-step

**Step1:** Cannot be solved by recalling "multiply-claimed -> e2fsck -fy". That named fix is textbook and produces WRONG output (victim holds aggressor bytes, real data deleted). Requires fusing two independent fsck signals (duplicate + leak) and structural victim direction (interior of contiguous run owns run). Name-the-bug gives correctly "cross-linked block" but fix is not e2fsck clone. Empirically discovered only by od/hexdump + extent walk + bitmap scan.

**Step2:** Recall "parse extents inline in i_block" is insufficient for held-out with varying layouts; textbook code snippet that assumes group descriptor size 32 and inode table at fixed place fails on different mkfs layout. Must probe superblock fields `s_log_block_size`, `s_inodes_per_group`, `bg_inode_table_lo`, `s_first_data_block`. Overfit-proof via held-out disjoint content/layout — memorizing sample offsets fails.

**Step3:** Recall "leaked block is unreferenced allocated" commonly taught as "free it". Here some leaks must be freed, one must be assigned to victim. Distinguishing requires matching `i_blocks`/`i_size` and not assuming count==1. Also extent index traversal is not recalled from simple ext4 tutorials which often show only inline depth-0 examples. Need to implement index leaf walk, which fails if only inline case memorized.

**Cross-step:** Requires carrying understanding that leak IS data, not garbage, from step1 to step2, but then overriding that "all leaks are data" to "some leaks are garbage to free" in step3. Solver who glues interior heuristic from step2 without adaptation fails step3 because interior check alone insufficient when multiple single-block inodes exist and need size coherence. Over-pinning step2's "bitmap needs no edit" as invariant fails step3.

## Partial failure modes (>=1/5 frontier)

- Step1 ≥1/5: runs e2fsck -fy and stops (consistent but content wrong), or byte-patches wrong inode direction, or hardcodes example offsets. Predict 2/5 frontier fail.
- Step2 ≥1/5: builds `/solution/repair` that hardcodes disk.img's dup block number D and leaked P_B; passes local disk.img (since same image) but fails on held-out hidden image with different numbers (victim sha mismatch). Or builds repair that clones D instead of rethreading to leak. Predict 2/5 fail among those reaching step2.
- Step3 ≥1/5: keeps depth==0 parser, so held-out deep-extent image stays multiply-claimed (fsck still reports dup). Or picks wrong leaked block among multiple leaks (chooses genuine orphan), victim content = orphan zero/old data, not original, content RED. Or fails to clear remaining genuine leaks, fsck reports "unreferenced block" → not clean.
- Cross-step ≥1/5: step2 tool overwrites bitmap clearing logic too early, or step1 creates `/solution/repair` (over-exec) that lacks deep walk and then step3 tries to patch but leaves old code path reachable causing flaky content. Or loses executable permission on `/solution/repair` across sessions (inherit_prior_session true but file deleted).

## Predicted per-model cascade rates (before build)

- Weak tester (reaches for e2fsck, cannot write python byte-patcher without mount knowledge): Step1 0/5, Step2 0/5 conditional, Step3 0/5. Overall 0/5 reach end.
- Frontier (Opus/GPT-class, careful, knows ext4 format): Step1 ~3/5 (fails 2/5 to e2fsck clone/wrong direction/hardcode). Among those passing S1, Step2 ~2/3 (fails 1/3 to hardcoding or clone heuristic). Among those reaching S2, Step3 ~2/2? Actually need at least 1 fail ≥1/5: Step3 ~1/2 pass for frontier because deep extent + multi-leak disambiguation is hard; predicts 2/4 fail to wrong leak pick or missing index walk. So cascade: Avocado tries 5 → 3 reach S2 → 2 reach S3 → 1 finish. Meets calibration: weak mostly fails per step, ≥1 strong passes ≥1/5 and fails ≥1/5 among trials reaching it, Avocado must reach last step at least once (need careful but reachable).
- Stronger variant if depth>0 is quite hard may be 1/5 final, still meets ≥1/5 pass at each step among early denominators.

## Cross-step S1/S2/S3 coupling (why not decorative)

- S1->S2: S1 oracle coupling: step2 tool must reuse step1's discovered logic (ref map + leak via bitmap) to repair arbitrary image. Step2's hidden test runs `/solution/repair <scratch>` artifact built in S1+S2 on held-out image and checks its output. Without S1's logic, S2 cannot pass. S2 instruction does not repeat S1's interior-run victim-direction reasoning (S2 non-duplication: it says "using same logic you used" terse, not re-pinning superblock offsets). S3 test adaptation verifies S2 artifact works on old single-leak case too (regression) — specific to S1 output.

- S2->S3: S1 oracle? S2->S3 coupling: S3 oracle uses S2's `/solution/repair` binary and expects it to now handle deep extents + multi-leak. S2 instruction did not mention index blocks or multiple leaks, so S3 is non-trivial pivot (overriding). S2->S3 S2 non-duplication: S3 does not restate `repair <path>` contract anew beyond saying "rework" — relies on carried context that tool exists at `/solution/repair` and usage shape. S3 test adaptation: asserts old shortcut code paths absent (`depth == 0` assumption, `len(leaked)==1` assert) — verifies adaptation to specific prior output's limitation.

Why not decorative: Would 3 single-turn tasks be just as good? No, because step2 builds on step1's fix (same image class, same file-system, same tooling) and step3 invalidates step2's heuristic that previously passed. Over-execution guard relies on not knowing future requirements.

## Hidden-test plan per step (overfit-proof, held-out disjoint)

Fixtures off agent-writable `/app`: under `/opt/holdout/` root-owned 700 baked at image build time, plus test-owned `/tests/` that copies images to tmp controlled by test so agent cannot pre-patch.

**Step1 hidden tests:**
- Ground truth manifest for `/work/disk.img`: for each regular file inode, sha256 of true original content (from author synthesis). Also records which inode is victim B, aggressor A, true P_B, dup D.
- Test copies? No, step1 fixes in place: after solver runs, extract every file via `debugfs -R "dump <path>"` without mount (or raw extent walk) and compare sha256 to manifest. Victim must match original, not aggressor bytes. Aggressor must be unchanged vs manifest. All other files unchanged.
- Also `fsck.ext4 -n /work/disk.img` must exit 0 and report no errors (no multiply-claimed, no leaked, no bad i_blocks). Positive case naive e2fsck clone fails content sha but passes fsck clean — so content check is load-bearing second assertion.
- Sample `/work/example/` disjoint from target ensures overfit fails.

**Step2 hidden tests:**
- Held-out broken images (≥2 instances) under `/opt/holdout/`: `heldout_broken_0.img`, `heldout_broken_1.img` with different block counts, file counts, contents, k interior offset, victim/aggressor paths disjoint from shipped sample and target. Each has manifest `heldout_manifest_*.json` with per-inode sha256 original, A path, B path, P_B, D.
- Procedure per held-out: copy broken to scratch `/tmp/repair_test_*.img`, run `/solution/repair <scratch>`, assert exit 0, assert for every regular file inode extracted sha256 == manifest original, assert victim == original not aggressor, assert `fsck.ext4 -n` clean. Also assert tool did not modify other files' content beyond victim fix.
- Second held-out instance has different interior offset k and different victim direction (e.g., aggressor in different block group) to guard assuming fixed k or lower inode number.
- Anti-reward-hacking: tool's actual binary runs, not existence check; byte-exact sha against hidden originals; multiple disjoint images block hardcoding; executable bit check on `/solution/repair`.

**Step3 hidden tests:**
- New held-out set `heldout_deep_*.img` and `heldout_multi_leak_*.img`:
  - Deep variant: at least one of A/B extents stored in index leaf block (depth=1). Built by creating many files to force extent tree growth or using larger file that forces leaf. Victim still single-block, aggressor >=4 blocks but its extent in leaf. Tool must walk index to find dup.
  - Multi-leak variant: image contains 2-3 leaked blocks — one is victim's P_B, others are genuine orphans from previous deletes (random blocks allocated then unlinked, bitmap left set). Correct behavior: rethread victim to P_B, free other leaks (clear bitmap bits). Manifest records which leaked is victim's real data vs which are orphans to free.
- Tests: for each variant copy to scratch, run `/solution/repair <scratch>`, assert all file shas match originals (victim original, aggressor unchanged, other files unchanged), assert fsck clean (no dup, no leaked), assert block bitmap correctly cleared for orphan leaks (re-read bitmap vs refset — no unreferenced allocated blocks remain).
- Regression: also re-run step2 single-leak inline held-out to ensure step3 tool still passes old class (backwards compatibility required for genuine victims).
- Absence assertions: inspect `/solution/repair` source (if python) or binary strings for overly narrow assumptions? Instead behavioral: if tool assumes depth==0, deep case fsck still reports multiply-claimed → RED; if assumes single leak, multi-leak case either leaves leak or assigns wrong block → content or fsck RED. Additional check that tool does not contain hard-coded check `assert len(leaked)==1` by attempting multi-leak where that would abort.
- Parametrized labels: not classification, but per-file sha checks balanced (victim vs aggressor vs other) — majority predict (e.g., always return aggressor bytes) fails victim check.

**Over-execution negatives (identifiers drawn ONLY from later steps instruction.md verbatim):**

From step2 instruction.md explicitly names `/solution/repair` and `repair <image_path>`. So step1 over-exec negative: step1 must NOT create file `/solution/repair` nor file at path `/solution/repair` containing repair logic — test at step1 stage asserts `/solution/repair` does not exist (or not executable) yet, because that belongs to step2. If agent does next step early (creates tool in step1), trips negative.

From step3 instruction.md explicitly names identifiers: depth, `i_block`, `ee_len`, `block bitmap`, "index", "free". But over-exec map rule requires exact identifiers later instruction explicitly names: we pick file path `/solution/repair` is also in step3, but over-exec for step2 should be from step3 identifiers: e.g., step2 must not contain handling for "index blocks" or "freeing genuine leaks" that would be over-execution? However spec says over-exec negatives from later identifiers ONLY — draw from later instruction verbatim names (function, config key, file path, class, table column). So:

- overExecMap: "1": ["/solution/repair"] (file path explicitly named in step2)
- overExecMap: "2": ["/solution/repair"] is still future? Actually step3 also names `/solution/repair` — but that's same file, not over-exec. Better pick for step2 over-exec: step2 should not yet handle "index" or "clearing bits" or depth>0 logic — but identifier must be from step3 instruction.md verbatim. Step3 names `/solution/repair` again, but over-exec for step2 could be checked via behavior: if step2 tool already passes deep-extent test, it did next step early — but we want negative test that asserts step2 tool does NOT need to pass deep case yet. However classical over-exec negative is file existence or content string that appears only in later step instruction. Since `/solution/repair` exists in both step2 and step3, not good to use for step2 negative. Instead we can use identifier "free" or "bitmap" — but file path is stronger.

Simplify: define overExecMap as:
- 1: ["/solution/repair"]  (step1 must not create repair tool)
- 2: ["/solution/repair"] can't use same — let's use something else: step3 introduces concept of "deep extents" and mentions "clearing their bits in the block bitmaps" and "index blocks". Could use a marker file that later step would create? But spec says over-exec negatives drawn ONLY from later identifiers explicitly named. Could still use function name if we define? However step3 instruction does not name a new file path besides `/solution/repair`. The over-exec for step2 could be that tool must NOT yet correctly handle multi-leak case — i.e., running repair on multi-leak image at step2 stage should still leave fsck not clean (since not required yet). But that is not a file-path negative.

To satisfy format, we will list overExecMap:
- 1: ["/solution/repair"]
- 2: ["/solution/repair"] is technically allowed but redundant; we will instead point to absence of old shortcuts: step2 tool contains string "depth" handling? That's from step3. But for compliance, we can have step2 over-exec check that `/solution/repair` when inspected does not need to handle "index" — but simplest: step2 negative is that a hypothetical marker for step3 e.g., if agent creates a file `/tmp/deep_fixed` early. Instead we can define overExecMap 2 as ["/solution/repair"] still valid if we interpret as step2 should not be overwritten? Might need distinct.

Better: Keep overExecMap simple: step1 must not have `/solution/repair`; step2 must not handle deep case already (behavioral negative, not file). For file-based map we can still list `/solution/repair` for step1 only.

We will document over-exec negatives as: step1 asserts `/solution/repair` absent; step2 asserts that running repair on deep-extent held-out still fails (since deep handling not yet required) — this checks agent didn't over-execute step3 early. That's guardable.

**Regression checks:**
- After step2, re-check `/work/disk.img` still fixed (content + fsck clean) — ensures step2 didn't break prior.
- After step3, re-check both old single-leak inline held-out and `/work/disk.img` still pass — ensures pivot didn't regress previous class.

## Cascade calibration plan

- Step1 calibration: ≥1 pass ≥1 fail among 5 trials reaching it — ensured by e2fsck trap and wrong-direction trap. Weak 0/5, frontier 3/5.
- Step2 calibration: denominator = trials that passed S1. Among those, ≥1 fail to hardcoding/clone heuristic, ≥1 pass with generic parser. Target 2/3 pass.
- Step3 calibration: denominator = trials reaching S3 (passed S2). Need ≥1 pass (full tree walk + selective leak assign+free) and ≥1 fail (depth-only miss or wrong leak pick). Frontier ~1/2. Avocado must reach last step at least once (our predicted 1-2 out of 5 total finish). min_reward=1.0 cascade ensures partial credit per step but final needs all.

If early filter too hard (S1 0/5), relax by providing example pair with clearer diff; if late step masks earlier (S3 0/5 but S1/S2 5/5), then earlier verifier checks validity not quality — tighten earlier? Actually earlier already had signal, so S3 0/5 indicates deep variant too hard — reduce depth to 1 only not 2, or reduce multi-leak to 2 not 3.

## Environment spec

FROM public.ecr.aws/docker/library/python:3.11-slim
- apt-get update && apt-get install -y --no-install-recommends e2fsprogs=1.47.0-2+deb12u1 debugfs? (e2fsprogs includes debugfs, fsck.ext4, mke2fs) coreutils util-linux file
- pip install pytest==8.3.4 struct (stdlib) — no extra deps needed but include pytest
- deterministic mtimes: use `faketime "2020-01-01 00:00:00"` during image synthesis
- planted state: `/work/disk.img` (target broken), `/work/example/broken.img`, `/work/example/original.img` built deterministically: mke2fs -F -q -b 4096 -O extent,^metadata_csum,^64bit -U fixed-uuid -E root_owner=0:0 <img> <blocks>, populate files via debugfs write, content seeded PRNG per instance, ensure aggressor >=16KiB contiguous single extent, victim single-block outside run, plant corruption via python byte-patcher overwriting ee_start to D=S+k interior. Sanity fsck -n reports multiply-claimed + leaked, cat victim returns aggressor bytes. Hidden held-out images under /opt/holdout root:root 700: heldout_broken_*.img + manifest json, heldout_deep_*.img, heldout_multi_leak_*.img. Canary GUID baked into root-owned /opt/holdout/.canary file.
- allow_internet false — no network needed, pip deps pinned offline.
- No prior-run artifacts in env.

## task.toml skeleton shape (already written, tags BEFORE steps, 1.1)

See task.toml file.

## Oracle-chain sketch per step (self-contained, no starved resource)

**Step1 oracle solve.sh:**
- parse superblock at 1024, get block size, blocks_per_group, inodes_per_group, inode_size, first_data_block, gdt block
- for each group read bg_inode_table_lo, iterate inodes, check links>0 and EXT4_EXTENTS_FL, parse i_block[0:60] extent header (magic F30A depth 0 ents), collect extents (eb, el, start, off_in_iblock)
- build ref map phys->owners, find dup block D where len>1
- victim = owner where el==1 and other owner el>=4 and D in interior (D != start and D != start+len-1 for aggressor)
- find leaked: scan each group's block bitmap block, for each bit allocated but not in ref, collect
- assert 1 leaked P_B
- patch victim inode's ee_start_lo/hi at inode_off+40+off+8/+6 to P_B via r+b write
- fsck should now clean

**Step2 oracle:**
- cat > /solution/repair <<'PY' python generic version of above (support any layout, no hardcode), chmod +x, run `/solution/repair /work/disk.img`
- repair script parses sb/gdt generic, builds ref, finds dup, identifies victim via interior check + single-block size, finds leaked via bitmap scan, rethreads victim ee_start to leaked, writes image.

**Step3 oracle:**
- upgrade repair script to depth>0: implement recursive walk for extent index nodes: if header depth>0, each index entry at offset 12+i*12 has ei_block, ei_leaf_lo/hi, read block at leaf, if its header depth==0 collect extents, else recurse.
- for leak selection: after building ref, gather all leaked blocks; for each leaked, heuristic: if leaked block count + other counted blocks would satisfy victim's i_blocks (single), candidate. Among candidates, prefer one where content size plausible (if victim size less than block size, any leaked works but still need deterministic pick). In multi-leak case, one leaked will match victim's size expectation (victim single), others are genuine orphans -> after rethread, rebuild ref, for any remaining leaked, clear bitmap bits: open image r+b, read bitmap block, clear bit `bm[bit>>3] &= ~(1<<(bit&7))`, write back.
- also need to update block group checksum? Since metadata_csum off, no need.
- after patch, fsck clean, all file shas correct
- chmod +x /solution/repair

All steps self-contained given declared outputs, no starved resource (disk.img persists, example pair read-only, /solution dir writable).

## What omitted vs kept per step

- Omitted from step1: cause file/fix name "ee_start rethread to leaked", group descriptor details, bitmap clearing (not needed), depth handling, generic tool path `/solution/repair` (belongs to step2). Kept: exact paths `/work/disk.img`, `/work/example/broken.img`, `/work/example/original.img`, symptom cross-linked + leaked, fsck reports multiply-claimed, auto-fix destroys data, no mount, in-place repair.
- Omitted from step2: interior-of-run reasoning, superblock field names, bitmap scan details (carried), deep extent handling, multi-leak disambiguation (future). Kept: `/solution/repair` path, usage `repair <image_path>`, generic requirement, executable, held-out grading mention, victim/original bytes contract, fsck clean.
- Omitted from step3: exact tree walk algorithm, size matching heuristic details (should be inferred probing), but kept: depth>0 index blocks, multiple leaked blocks genuine vs victim, must free genuine leaks by clearing bits, drop assumptions depth==0, len(leaked)==1, any leak == victim, must still handle old class, same `/solution/repair` path and usage.

## Canary GUID

ac3c809e pooled fresh -> TBENCH-MT-FSINT-XLINK-24-ac3c809e-ad1b-475d-a562-0488d8299043 copied into task.toml and will be copied into final Dockerfile + solve.sh + test.sh by Codex.
