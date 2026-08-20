import json,sys
events=[json.loads(line) for line in open(sys.argv[1]) if line.strip()]
json.dump([],open(sys.argv[2],"w"),separators=(",",":"))
