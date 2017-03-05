def check_image_size(filepath):
    import numpy as np
    import nibabel as nb
    img = nb.load(filepath)
    return np.sum(img.get_data() > 0)
