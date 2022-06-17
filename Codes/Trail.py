import time
import threading


class Queue:
    def __init__(self):
        self.nums = [0] * 10

    def add(self, item):
        self.nums.append(item)
        print(f'{item} appended')

    def get(self):
        res = self.nums.pop(0)
        print(f'{res} popped')


Q = Queue()
signal = True


def auto_add():
    while signal:
        Q.add(1)


def auto_get():
    if len(Q.nums) > 0:
        Q.get()


t = threading.Thread(target=auto_add)
t.start()
for i in range(50):
    auto_get()
signal = False
