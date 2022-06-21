import copy
import random
import time
import numpy as np
REDTEXT = '\33[31m'
WHITETEXT = '\33[39m'


class Span:
    def __init__(self, start, stop):
        assert start <= stop
        self.start = start
        self.stop = stop
        self.span = self.stop - self.start
        self.cntr = (self.start + self.stop) / 2

    def __contains__(self, val):
        return self.start <= val < self.stop

    def adjacent(self, val):
        return self.start <= val <= self.stop

    def overlap_span(self, other: 'Span') -> 'Span | None':
        if self.start < other.stop:
            return Span(self.start, other.stop)
        if other.start < self.stop:
            return Span(other.start, self.stop)
        return


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
        s = Span(1, 4)
