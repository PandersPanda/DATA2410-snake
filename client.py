import random
import tkinter
import grpc
import snake_pb2
import snake_pb2_grpc
import time


SNAKE_SIZE = 20
GAME_SPEED = 50

GAME_WIDTH = 600
GAME_HEIGHT = 620

root = tkinter.Tk()
root.resizable(False, False)
root.title("Snake Game")

canvas = tkinter.Canvas(width=GAME_WIDTH, height=GAME_HEIGHT, highlightthickness=0, background='black')

channel = grpc.insecure_channel('localhost:50051')
stub = snake_pb2_grpc.SnakeServiceStub(channel)
snake = stub.addSnake(snake_pb2.JoinRequest())
direction = snake.direction


def draw_snake(s):
    for p in s.body:
        canvas.create_rectangle(
            p.x * SNAKE_SIZE,
            p.y * SNAKE_SIZE,
            (p.x + 1) * SNAKE_SIZE,
            (p.y + 1) * SNAKE_SIZE,
            fill=s.color,
            tag='snake'
        )


draw_snake(snake)


def move_snake():
    global snake
    snake = stub.moveSnake(
        snake_pb2.MoveRequest(color=snake.color, direction=direction)
    )


def change_direction(event):
    global direction
    direction = event.keysym


def check_collision():
    has_collided = stub.checkCollision(
        snake_pb2.CollisionRequest(color=snake.color)
    )
    return has_collided.has_collided


def draw_all_snakes():
    canvas.delete('snake')
    snakes = stub.getSnakes(snake_pb2.GetRequest())
    for s in snakes:
        draw_snake(s)


canvas.bind_all('<Key>', change_direction)


def game_flow():
    global snake
    if check_collision():
        root.quit()
    move_snake()
    draw_all_snakes()
    canvas.after(GAME_SPEED, game_flow)


game_flow()
canvas.pack()
root.mainloop()
