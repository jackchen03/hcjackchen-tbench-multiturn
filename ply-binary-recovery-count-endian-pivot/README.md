# PLY binary recovery count/endian pivot

This three-step task carries recovered mesh geometry through area-weighted normal enrichment, then deliberately replaces the binary colored mesh with an ASCII oriented point cloud.

## Context chain

1. Step 1 repairs coupled binary framing and field-endian corruption while preserving vertex and face order.
2. Step 2 consumes that recovered mesh, preserves its exact geometry/topology, and adds normals plus a validity report.
3. Step 3 consumes the enriched artifact, preserves xyz/normals, and removes the binary, color, and face representation.

The chain is non-decorative because normal correctness depends on recovered faces and positions, while the final artifact must retain step-2 normals yet remove properties introduced or retained earlier.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only reference behavior and boundary enforcement, not model calibration.
