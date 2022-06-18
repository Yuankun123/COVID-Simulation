def generator(a):
    for i in range(a):
        yield i


for k in generator(5):
    print(k)