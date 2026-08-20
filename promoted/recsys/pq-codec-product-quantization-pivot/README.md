# PQ codec product quantization pivot

Step 1 establishes a self-consistent compressed vector store, step 2 carries its decoded vectors into top-k retrieval, and step 3 replaces both with the explicitly specified ISQ1 scalar format.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

