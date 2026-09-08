# Custody incident event format

Every case directory contains UTF-8 JSON Lines files. Blank lines are ignored; a
non-object JSON value, a missing required field, a duplicate immutable ID, or an
invalid signed record is malformed evidence and the command must exit nonzero.

`physical_nodes.jsonl` records have `node_id`, `node_kind`, `specimen_id`,
`initial_quantity_ul`, `retained_quantity_ul`, `consumed_quantity_ul`, and
`tainted_initial`. Quantities are nonnegative integers. Conservation means a
node's initial quantity equals its retained quantity, its consumed quantity,
and all authoritative outgoing `physical_material` quantities added together.
Taint starts at `tainted_initial` nodes and follows only `physical_material`
edges.

`operations.jsonl` records have `operation_id`, `command_digest`,
`execution_id`, `successful`, `input_position_id`, `output_position_id`,
`input_node_id`, `output_node_id`, `edge_type`, `quantity_ul`,
`input_barcode`, `output_barcode`, `timestamp`, and `sequence_counter`.
`receipts.jsonl` records have `receipt_id`, `command_digest`, `execution_id`,
`input_position_id`, `output_position_id`, and `quantity_ul`. A receipt is
complete only when those five values exactly match one successful operation.
Only complete receipts authorize operation edges. Failed attempts and display
fields never authorize an edge.

`results.jsonl` records have `result_id`, `original_result_id`, `specimen_id`,
`assay_id`, `assay_execution_id`, `physical_node_id`, and `rerun_id` (null for
an original result). Every result contributes an `analytical_derivation` edge
from its physical node to its result ID with quantity zero and null receipt.

Step-specific files may be absent. `reruns.jsonl` records have `rerun_id`,
`root_node_id`, sorted unique `node_ids`, sorted unique `boundary_node_ids`,
sorted unique `supersedes`, `issuer_id`, and base64 `signature`. A listed node
must be reachable from the root by reported custody edges without entering a
boundary. The root itself is reachable. A rerun result is eligible only when
its `physical_node_id` and the original result ID are both in the signed node
set. Signed overlap must have one active transitive supersession maximum;
otherwise the original result remains authoritative.

Rerun signatures cover exactly the bytes described in the step-2 request.
`revocations.jsonl` records have `revocation_id`, `rerun_id`, `issuer_id`, and
base64 `signature`, covering UTF-8 bytes
`CUSTODY-RERUN-REVOCATION-V1\nrevocation=<id>\nrerun=<id>\n`.
`issuers.json` maps issuer IDs to objects with `public_key_b64` (raw Ed25519
public-key bytes) and `roles`; the corresponding records require
`rerun_authority` or `revocation_authority` respectively.

`reagent_uses.jsonl` records have `assay_execution_id` and `lot_id`; each adds
a typed `reagent_use` edge from the lot to that execution. `invalid_lots.jsonl`
records have `lot_id` and boolean `active`. Assay minima are read from
`CASE_DIR/assay-minimums.json` when supplied, otherwise from
`/app/policies/assay-minimums.json`; each maps an assay ID to a nonnegative
integer number of microlitres.

Reports are deterministic UTF-8 JSON. Arrays are sorted lexically by their ID
fields (and `custody_edges` by edge type, from ID, to ID, quantity, then receipt
ID with null ordered before strings). Extra diagnostic top-level fields are
allowed if they do not alter the required fields.
