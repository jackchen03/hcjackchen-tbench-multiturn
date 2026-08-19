# Repeat shoppers deduplication pivot

The carried pipeline first canonicalizes SKU identities, then maps SKUs to purchased products for exclusion, and finally replaces SKU-only deduplication with product-level diversity.

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only reference behavior and boundary probes.

