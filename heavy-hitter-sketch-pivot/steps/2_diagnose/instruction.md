Your exact counter is correct but too slow on the full stream. Run `python3 /app/profile_driver.py --sample /app/stream_sample.txt --k 10` and write /app/diagnosis.json with exactly the keys hotspot, share, evidence, where hotspot names the slower stage, share is its fraction of total time between 0 and 1 and is at least 0.5, and evidence quotes the driver's timing lines.

The diagnosis file is the new behavior under check; exact counting behavior from step 1 remains in place and callable.
