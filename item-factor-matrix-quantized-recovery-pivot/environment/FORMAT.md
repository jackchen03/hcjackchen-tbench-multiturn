# Quantized item-factor checkpoint

`meta.json` gives `num_items`, `dim`, `m1`, and `k1`.
`stage1_codebook.bin` is little-endian float32 shaped `(m1,k1,dim/m1)`.
`stage1_codes.bin` is uint8 shaped `(num_items,m1)`.
Concatenating selected subspace centroids reconstructs the stage-one factor.

`aux.bin` is a reserved calibration block. Older readers may ignore it, although quality can drop for a small traffic segment.
