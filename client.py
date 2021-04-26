import tkinter
import snake_pb2
import snake_pb2_grpc
import grpc
import random

SNAKE_SIZE = 20
GAME_SPEED = 50

GAME_WIDTH = 600
GAME_HEIGHT = 620

root = tkinter.Tk()
root.resizable(False, False)
root.title("Snake Game")

canvas = tkinter.Canvas(width=GAME_WIDTH, height=GAME_HEIGHT, highlightthickness=0, background='black')

snake = snake_pb2.Snake(
    name="test_player",
    color="Red",
    size=3,
    direction="Right",
    body=[
        snake_pb2.Point(x=2, y=0),  # Head
        snake_pb2.Point(x=1, y=0),  # Body
        snake_pb2.Point(x=0, y=0)  # Tail
    ]
)

food = snake_pb2.Food(color='White', position=snake_pb2.Point(x=10, y=10))

channel = grpc.insecure_channel('localhost:50051')
stub = snake_pb2_grpc.SnakeGameServiceStub(channel)
stub.addSnake(snake)


def draw_snake():
    global canvas
    global snake

    canvas.delete("snake")

    for node in snake.body:
        canvas.create_rectangle(
            node.x * SNAKE_SIZE,
            node.y * SNAKE_SIZE,
            (node.x + 1) * SNAKE_SIZE,
            (node.y + 1) * SNAKE_SIZE,
            fill=snake.color,
            tag="snake"
        )


draw_snake()


def set_new_snake_direction(event):
    global snake
    snake.direction = event.keysym
    snake = stub.moveSnake(snake)


canvas.bind_all('<Key>', set_new_snake_direction)


def collision_check():
    global food, snake, root

    head_x = snake.body[0].x
    head_y = snake.body[0].y

    if snake.body[0] == food.position:
        new_head = snake_pb2.Point(x=head_x, y=head_y)
        snake.body.insert(0, new_head)
        stub.eatFood(snake)
        spawn_food()
        return False
    return head_x < 0 or head_x > 30 or head_y < 0 or head_y > 30


def move_snake():
    global snake
    if collision_check():
        return

    snake = stub.moveSnake(snake)
    draw_snake()

    # Collision check:
    canvas.after(GAME_SPEED, move_snake)


def spawn_food():
    global canvas
    global food
    canvas.delete("food")

    food_x = random.randint(0, GAME_WIDTH // SNAKE_SIZE - 1)
    food_y = random.randint(0, GAME_HEIGHT // SNAKE_SIZE - 1)

    while snake_pb2.Point(x=food_x, y=food_y) in snake.body:
        food_x = random.randint(0, GAME_WIDTH // SNAKE_SIZE - 1)
        food_y = random.randint(0, GAME_HEIGHT // SNAKE_SIZE - 1)
        snake_pb2.Point(x=food_x, y=food_y)

    food = stub.spawnFood(snake_pb2.Point(x=food_x, y=food_y))

    canvas.create_rectangle(
        food_x * SNAKE_SIZE,
        food_y * SNAKE_SIZE,
        (food_x + 1) * SNAKE_SIZE,
        (food_y + 1) * SNAKE_SIZE,
        fill=food.color,
        tag="food"
    )


spawn_food()
canvas.pack()
canvas.after(GAME_SPEED, move_snake)
root.mainloop()
