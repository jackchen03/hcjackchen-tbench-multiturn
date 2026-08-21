WEIGHTS = {"item_quality": 2.0, "u_cat_affinity": 3.0}


def score(row):
    return sum(row[name] * weight for name, weight in WEIGHTS.items())
