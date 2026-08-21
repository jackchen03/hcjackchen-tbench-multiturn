def base_score(user, item):
    return float(sum(a * b for a, b in zip(user["embedding"], item["embedding"])))
