"""Trail"""


class A:
    def __init__(self, k: list):
        self.k = k

    def __getitem__(self, item):
        print(item)
        return self.k[item]


a = A([1, 2, 3, 4])
print(a[1:3])
