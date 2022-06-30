"""Trail"""


class A:
    a = []

    def __init_subclass__(cls, **kwargs):
        cls.a = []


class B(A):
    pass


B.a.append(0)
print(A.a, B.a)