from benchopt import BaseDataset
from benchopt import safe_import_context

with safe_import_context() as import_ctx:
    import numpy as np
    from scipy.sparse import rand as sprand
    make_blur = import_ctx.import_from('shared', 'make_blur')


class Dataset(BaseDataset):

    name = "Simulated"

    # List of parameters to generate the datasets. The benchmark will consider
    # the cross product for each key in the dictionary.
    # A * I + noise ~ N(mu, sigma)
    parameters = {
        'std_noise': [0.3],
        'size_blur': [27],
        'std_blur': [2.],
        'subsampling': [4],
        'type_A': ['deblurring', 'denoising'],
    }

    def __init__(self, std_noise=0.24,
                 size_blur=27, std_blur=8.,
                 subsampling=4,
                 random_state=27,
                 type_A='denoising'):
        # Store the parameters of the dataset
        self.std_noise = std_noise
        self.size_blur = size_blur
        self.std_blur = std_blur
        self.subsampling = subsampling
        self.random_state = random_state
        self.type_A = type_A

    def set_A(self, height):
        return make_blur(self.type_A,
                         self.size_blur, self.std_blur,
                         height)

    def get_data(self):
        rng = np.random.RandomState(self.random_state)
        height, width = (64, 32)
        n_blocks = 5
        z = sprand(
            1, width, density=n_blocks/width,
            random_state=rng
        ).toarray()[0]
        img = (np.cumsum(rng.randn(height, width) * z, axis=1)
               [::self.subsampling, ::self.subsampling])
        A = self.set_A(img.shape[0])
        y_degraded = (A @ img +
                      rng.normal(0, self.std_noise, size=img.shape))
        data = dict(A=A, y=y_degraded)

        return data