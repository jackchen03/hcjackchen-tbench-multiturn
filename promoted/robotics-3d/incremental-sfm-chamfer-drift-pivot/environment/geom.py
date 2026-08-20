def datum_is_fixed(scene):
    return scene['camera0'].shape == (4,4) and float(scene['baseline'][0]) == 1.0
