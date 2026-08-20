import json
def load_index(path):
    return json.load(open(path+"/index.bin"))
def knn_search(idx,query_vec,k=10):
    rows=idx["slots"][:idx["node_count"]]
    return [row["item_id"] for row in sorted(rows,key=lambda r:sum((a-b)**2 for a,b in zip(r["vector"],query_vec)))[:k]]

