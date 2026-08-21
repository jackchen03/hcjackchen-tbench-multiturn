import json
def load_graph(path): return json.load(open(path+"/graph.bin"))
def knn_search(graph,q,k): return [node["item_id"] for node in reversed(graph["nodes"][:k])]
