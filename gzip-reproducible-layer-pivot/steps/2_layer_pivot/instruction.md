Byte-identical gzip is not enough anymore: downstream needs a content-addressed layer
whose entry order is derived from your manifest, as specified in /app/LAYER_SPEC.md,
which appears from this step on. Add `/app/make_layer.sh <srcdir> <manifest> <out.tar>`
producing the layer at /app/layer.tar covering exactly the manifest entries — no more
and no fewer, even if the source directory holds extra files the manifest does not
list.

The old gzip output may stay alongside; it is simply no longer the artifact of record.
