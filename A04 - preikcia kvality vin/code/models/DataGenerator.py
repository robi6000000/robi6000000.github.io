import numpy as np
from typing import List


class DataGenerator:
    betas: List[np.array]
    max_noise: int

    def __init__(self):
        self.betas = None
        self.max_noise = None

    def gen_2d_data(self, start: int, finish: int, size: int, noise=(0, 0)):
        beta0, beta1 = 0, 0
        while beta1 == 0:
            beta0, beta1 = np.random.randint(-5, 5, size=2)

        self.betas = [beta0, beta1]
        self.max_noise = noise

        x = np.random.randint(start, finish, size=size)
        mistake = np.random.randint(noise[0], noise[1], size=size)
        y = np.array([beta0 + beta1 * x[i] + mistake[i] for i in range(size)])
        return x, y

    def gen_3d_data(self, start: int, finish: int, size: int, noise=(0, 0)):
        beta0, beta1, beta2 = 0, 0, 0
        while beta1 == 0 or beta2 == 0:
            beta0, beta1, beta2 = np.random.randint(-10, 10, size=3)

        self.betas = [beta0, beta1, beta2]
        self.max_noise = noise

        x1 = np.random.randint(start, finish, size=size)
        x2 = np.random.randint(start, finish, size=size)

        mistake = np.random.randint(noise[0], noise[1], size=size)
        y = np.array([beta0 + beta1 * x1[i] + beta2 * x2[i] + mistake[i] for i in range(size)])
        return x1, x2, y
