# Cumulative build findings

| ID | Risk | Disposition | Evidence |
| --- | --- | --- | --- |
| F1 | Provisional byte anchors lose local-width metadata and zero-width markers | FIXED | Step-1 chain and semantic tests |
| F2 | A fused source set drops duplicate occurrences | FIXED | Step-2 ordered A-B-A test |
| F3 | Fused phases can inherit the wrong handler/root set | FIXED | Step-2 phase-local test |
| F4 | Required semantics could evade the size budget in an uncounted table | FIXED | independent inclusive accounting test |
| F5 | Public-sample hardcoding or no-op implementation | FIXED | disjoint hidden programs and DO-NOTHING phases |
| F6 | Step-2 change could regress Step-1 marker/width behavior | FIXED | named Step-2 regression test |
| F7 | Future capability could be unfairly banned in Step 1 | NOT_APPLICABLE | compatible early fusion is accepted; boundary recorded `NOT_REQUIRED` |
| F8 | Exact implementation representation could be over-graded | FIXED | behavioral CLI checks; no source/AST checks |

No open findings.
