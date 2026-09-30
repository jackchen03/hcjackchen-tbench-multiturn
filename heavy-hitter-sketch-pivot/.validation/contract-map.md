# Phase-2 contract map

Bundle fingerprint: `bundle-sha256-v1:35b8eb86a7efec7902cf03ef4c6270f067f01bfaac7dd25142f4ad3a41063e3a`

| Step | Contract | Authority | Shipped evidence |
| --- | --- | --- | --- |
| 1 | exact_topk accepts an iterable and k and returns exact [key,count] pairs | steps/1_exact/instruction.md:3 | public command plus disjoint seed 8/9 execution |
| 1 | ordering is count descending then key ascending | steps/1_exact/instruction.md:3 | moved planted ties in both hidden streams |
| 2 | diagnosis has exactly hotspot, share, evidence | steps/2_diagnose/instruction.md:1 | schema/type assertions |
| 2 | hotspot/share are relative measured stage attribution with share >= 0.5 | steps/2_diagnose/instruction.md:1 | independent driver rerun and tolerance |
| 2 | evidence quotes both driver timing lines | steps/2_diagnose/instruction.md:1 | timing-line parser with annotation allowed |
| 2 | exact counting remains callable and unchanged | steps/2_diagnose/instruction.md:3 | disjoint exact regression |
| 3 | approx_topk returns ten keys with recall >= 0.9 | steps/3_approx/instruction.md:1-3 | disjoint seed 8/9 truth |
| 3 | approximation peak is <= half exact reference peak | steps/3_approx/instruction.md:3 | tracemalloc median comparison |
| 3 | exact_topk remains callable | steps/3_approx/instruction.md:1 | disjoint exact regression |
| 3 | retirement has exact first line, benchmark milliseconds, own diagnosis citation | steps/3_approx/instruction.md:1-3 | format, factor-three provenance, carried comparison |

Non-unique surfaces are exercised by alternate stable sorting, quoted independent measurement, and compact array-backed Count-Min Sketch controls. Hidden streams change counts, membership, tie position, and layout from the public sample.
