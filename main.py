from snake_pb2 import Point

p1 = Point(x=1, y=1)
p2 = Point(x=1, y=2)

lp = [p1, p2]

print(p1 in lp)