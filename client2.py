import random
import tkinter
import grpc
import snake_pb2
import snake_pb2_grpc
import time
import threading
import sys

SNAKE_SIZE = 20
GAME_SPEED = 50

GAME_WIDTH = 620
GAME_HEIGHT = 620

root = tkinter.Tk()
root.geometry(f'{GAME_WIDTH}x{GAME_HEIGHT}')
root.resizable(False, False)
root.title("Snake Game")

canvas = tkinter.Canvas(width=GAME_WIDTH, height=GAME_HEIGHT, highlightthickness=0, background='grey6')
snake_body = [
    snake_pb2.Point(x=15, y=15),
    snake_pb2.Point(x=14, y=15),
    snake_pb2.Point(x=13, y=15),
    snake_pb2.Point(x=12, y=15),
    snake_pb2.Point(x=11, y=15),
    snake_pb2.Point(x=10, y=15),
    snake_pb2.Point(x=9, y=15),
    snake_pb2.Point(x=8, y=15)
]
snake_direction = 'Right'
scroll_region = 0.5


def draw_squares(point, r, color, tag=None):
    assert 0 < r <= 1

    food = canvas.create_rectangle(
        (point.x + .5 + r / 2) * SNAKE_SIZE,
        (point.y + .5 + r / 2) * SNAKE_SIZE,
        (point.x + .5 - r / 2) * SNAKE_SIZE,
        (point.y + .5 - r / 2) * SNAKE_SIZE,
        fill=color,
        tag=tag
    )
    canvas.tag_lower(food)


def draw_snake(body):
    for p in body:
        draw_squares(p, 1, color='red', tag='snake')


def game_flow():
    global scroll_region
    print(scroll_region)
    scroll_region = scroll_region - 1/62 if scroll_region > 0 else 0.5
    canvas.xview_moveto(scroll_region)
    canvas.after(GAME_SPEED, game_flow)


canvas.pack()
canvas.config(scrollregion=[0, 0, GAME_WIDTH*2, GAME_HEIGHT*2])
draw_snake(snake_body)
draw_squares(snake_pb2.Point(x=40, y=15), r=1, color='white')
game_flow()
root.mainloop()
