# Overflow largest-first heap tuple writer

Your current /app/encoder passes small rows but now fails rows that are close to the page limit. When the tuple would grow beyond 140 bytes, the legacy writer spills some text columns to external storage and replaces them with an 18-byte overflow pointer.

Extend the same executable at /app/encoder to handle those large rows. The spill decision is iterative and global: compute size with all text inline, while total_size > 140 pick the not-yet-overflowed non-null text column with the largest inline stored size (header plus raw bytes); ties go to the lowest column index; convert it to an 18-byte pointer and recompute total_size because padding of later columns shifts. Stop when total_size <= 140 or no text remains.

Each overflow pointer is [0x01,0x12,rawsize:u32 LE,extsize:u32 LE,valueid:u32 LE,toastrelid:u32 LE] where rawsize=extsize=len(value), toastrelid=0x0BADF00D constant, valueid is a global counter starting at 1000 plus one per overflowed value assigned in row order then column order.

Do not re-derive the alignment table, bitmap sizing, or text header threshold from scratch — you already have the area and conventions from step 1. Keep the same input JSON at stdin and same binary stream with 2-byte LE length prefix at stdout, and keep the binary at /app/encoder.

This step is about overflow handling that relies on accurate size accounting from prior layout work.

Title must mention overflow and heap tuple.
