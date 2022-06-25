import copy
import random
import time
import numpy as np


class Span:
    def __init__(self, start: float = 0, stop: float = 0):
        assert stop >= start
        self.start = start
        self.stop = stop
        self.span: float = self.stop - self.start
        self.cntr: float = (self.start + self.stop) / 2

    def __contains__(self, val):
        return self.start <= val < self.stop

    def adjacent(self, val):
        return self.start <= val <= self.stop

    def overlapped_span(self, other: 'Span') -> 'Span | None':
        start = max(self.start, other.start)
        stop = min(self.stop, other.stop)
        if start <= stop:
            return Span(start, stop)

    def __repr__(self):
        return f'Span({self.start}, {self.stop})'


def red_text(pale_str: str):
    return f'\33[31m{pale_str}\33[39m'


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
    s = Span(new_tuple=(1, 4))
    print(s)
