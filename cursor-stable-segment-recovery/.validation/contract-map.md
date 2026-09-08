# Phase-2 contract map

Fingerprint binding is added after the final bundle is frozen.

| ID | Step | Assertion or hidden dimension | Solver-visible authority | Evidence |
| --- | --- | --- | --- | --- |
| C01 | 1 | sealed, checksum-valid coherent manifest authority | instruction “under the format contract”; `FORMAT.md` Manifest ring | hidden cases include newer unsealed and stale/disconnected slots |
| C02 | 1 | authenticated scan after bounded corruption | instruction “records after bounded damage”; `FORMAT.md` Frames | valid-CRC wrong-predecessor decoy precedes a declared anchor |
| C03 | 1 | split data/control envelope reconstruction | instruction “transactions split across records or segment files”; `FORMAT.md` Frames | hidden cross-segment data and independent controls |
| C04 | 1 | full branch/generation/ID/incarnation identity | instruction “reused transaction IDs”; `FORMAT.md` transaction identity | accepted reused IDs with distinct incarnations plus stale lineage |
| C05 | 1 | commit/abort/ack precedence | instruction “all and only acknowledged”; `FORMAT.md` transaction rule | accepted, aborted, and missing-ack decisions |
| C06 | 1 | deterministic STATE/DECISIONS/PROVENANCE and exact original intervals | instruction second paragraph; `FORMAT.md` Recovery interface | canonical bytes, repeat run, independent interval map |
| C07 | 2 | immutable manifest and segment bytes | instruction “every source byte”; `FORMAT.md` view | before/after SHA-256 map and tamper rejection |
| C08 | 2 | exact carried decision digest | instruction “exact recovery decisions already produced”; `FORMAT.md` view | digest over unchanged Step-1 decision bytes |
| C09 | 2 | transaction-atomic continuation cursor | instruction enumerates continuation positions; `FORMAT.md` cursor rule | cursor inside accepted data interval resumes before transaction |
| C10 | 2 | rejected/aborted material contributes no replay item | instruction enumerates aborted positions; `FORMAT.md` cursor rule | cursor inside aborted envelope preserves accepted boundary |
| C11 | 2 | corruption-adjacent cursor advances by authenticated source order | instruction enumerates adjacent-to-corruption positions; `FORMAT.md` cursor rule | cursor in bounded pocket resumes at next accepted item |
| C12 | 2 | stale generation follows one manifest bridge | instruction enumerates stale generations; `FORMAT.md` bridge rule | disjoint stale cursor resolves to declared logical boundary |
| C13 | 2 | exact replay suffix without omission/duplication | instruction second paragraph; `FORMAT.md` output schema | every probe compares full identity suffix |
| C14 | both | hidden identifiers/layouts are disjoint from public fixture | `FORMAT.md` defines format; instructions require general behavior | hidden seeds/branches/payloads/offsets differ from public fixture |

Non-unique implementation surfaces are parser architecture, frame scanning,
decision reduction, interval indexing, helper names, and optional diagnostics.
The grader observes only contract outputs and runs no source-shape checks.
Alternate-control evidence is recorded separately after proof.
