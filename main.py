def recurrence(n):
    print(f"{(n - 4) * (n + 4)}c_{n} \t = \t {2 * (n + 2) * (n + 1)}c_{n + 2}")


for i in range(10):
    recurrence(i)
d = {
    1: 'One',
    2: 'Two',
    3: 'Three'
}

for n in d:
    print(n)