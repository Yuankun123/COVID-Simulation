import copy
import random
import numpy as np
from numpy.linalg import norm


def unit_vector(vector: np.ndarray) -> np.ndarray:
    temp = norm(vector, 2)
    if temp != 0:
        return vector / temp
    return np.array([0., 0.])


def rand_rearrange(input_list: list):
    """
    :param input_list: 输入列表
    :return: None
    """
    remaining_index = list(range(len(input_list)))
    copy_list = copy.copy(input_list)
    for i in range(len(copy_list)):
        input_list[i] = copy_list[remaining_index.pop(random.randint(0, len(remaining_index) - 1))]
