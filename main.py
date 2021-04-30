import random

li = [0, 1, 2, 3, 4, 5, 6, 7]


def stream_test():
    for i in li:
        yield i


s = stream_test()

empty = []

print(random.choice([]))


