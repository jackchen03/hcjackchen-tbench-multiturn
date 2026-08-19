# Phase-1 Step-2/Step-3 chain contradiction

Phase 2 stopped before bundle construction because the middle step has no coherent new outcome and the final pivot assumes behavior that the prior contracts forbid.

- Step 1 already requires restoring only the clobbered four-byte dirent inode field, explicitly without modifying `i_links_count` or `file_type`. For the declared sole corruption type, that restoration makes the original stored link counts equal the corrected reference counts.
- Step 2 asks to add link-count reconciliation, but also requires byte identity and says reconciliation must occur through the same dirent restoration rather than setting counts. With no additional corruption type, this is exactly Step 1 again.
- The environment explicitly says not to invent corruption beyond the four-byte dirent inode overwrite. The dossier nevertheless proposes secondary link-count corruption to make Step 2 substantive, then elsewhere says to keep the same corruption type and admits the Step-2 oracle can be the same as Step 1.
- Step 3 assumes the Step-2 implementation rewrites `i_links_count` and `file_type`, then requires removing those writes. Such writes would already violate Step 1 and Step 2's byte-identical contracts, so the purported pivot is from a noncompliant implementation rather than from the required Step-2 outcome.

Phase 1 must choose one coherent design: either introduce and authorize a distinct Step-2 corruption requiring actual link-count repair (and adjust byte-exact originals accordingly), or remove Step 2 / replace it with a genuinely additive outcome. Step 3 must then override behavior that was actually required by the corrected Step 2.
