Implement python3 rebuild.py <in.bin> <out.bin> so its output is byte-identical to /opt/ref/bin/slabcompact on any fragmented page, checked with cmp and computed directly without shelling out to slabcompact.

Grading runs your rebuild.py in an image where /opt/ref is absent, so any delegation to the reference binary fails. Your S1 and S2 reports stay on disk as reference but only rebuild.py output counts.
