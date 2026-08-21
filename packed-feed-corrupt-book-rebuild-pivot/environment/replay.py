import json,sys
json.dump({},open(sys.argv[2],"w"),sort_keys=True,separators=(",",":"))
