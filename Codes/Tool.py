import copy
import random
import time

import numpy as np


def unit_vector(vector: np.ndarray) -> np.ndarray:
    temp = norm(vector)
    if temp != 0:
        return vector / temp
    return np.array([0., 0.])


def rand_rearrange(input_list: list):
    """
    :param input_list: 输入列表
    :return: None
    """
    res = []
    input_list = copy.copy(input_list)
    while len(input_list) > 0:
        random.seed(time.perf_counter())
        res.append(input_list.pop(random.randint(0, len(input_list) - 1)))
    return res


def norm(input_array: np.ndarray) -> float:
    return (input_array[0] ** 2 + input_array[1] ** 2) ** 0.5


if __name__ == '__main__':
    class _Test:
        print(rand_rearrange([1, 2, 3, 4]))
