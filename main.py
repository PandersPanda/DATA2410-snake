directions = ['Left', 'Up', 'Right', 'Down']

course = 'Right'
dir_index = directions.index(course)

x, y = 2, 3

if dir_index % 2 == 0:
    x += -1 if dir_index < 2 else 1
else:
    y += -1 if dir_index < 2 else 1

print(x, y)


