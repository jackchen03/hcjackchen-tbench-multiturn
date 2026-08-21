# Core layout byte-exact heap tuple writer

We have a long-lived heap tuple writer that serializes a row into a tight binary tuple for disk pages. A rewrite attempt produces tuples that our page validator rejects as malformed, and columns land on wrong offsets, yet a single row's hexdump often looks normal. The bug only surfaces when you compare byte-for-byte against the old writer across many schemas and data.

The old writer is still in the environment at /verifier/legacy_writer. It reads stdin JSON of form {"schema": ["int8","text",...], "rows": [[...],[...]]} where types include int2,int4,int8,float8,point3,ts,text, values are JSON numbers for fixed types, base64 strings for text, and null for NULL. It writes to stdout a binary stream: for each row a 2-byte little-endian tuple length, then the tuple bytes, concatenated. Samples you can run are under /app/samples/ with several example inputs.

Build an executable at /app/encoder that accepts exactly the same stdin and produces exactly the same stdout bytes as /verifier/legacy_writer. For this first stage focus on rows that stay small — total tuple size at most 140 bytes where no spill to external storage happens. Hidden tests in this stage only contain those small rows, but they exercise all types including point3 and early NULLs that shift layout.

Your encoder must be byte-identical to the legacy writer on those small rows; the legacy writer will be removed during grading so your program must implement the format itself, not call it at runtime.

Title keywords heap, tuple, writer, byte must appear in description but the work here is probing and implementing core byte layout.
