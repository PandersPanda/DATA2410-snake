import random
import tkinter
from Snake import Snake, Food

SNAKE_SIZE = 20
GAME_SPEED = 200

GAME_WIDTH = 600
GAME_HEIGHT = 620

root = tkinter.Tk()
root.resizable(False, False)
root.title("Snake Game")

snake = Snake("Red")

canvas = tkinter.Canvas(width=GAME_WIDTH, height=GAME_HEIGHT, highlightthickness=0, background='black')


def draw_snake():
    global canvas
    global snake

    canvas.delete("snake")

    for node in snake.body:
        node_x, node_y = node
        canvas.create_rectangle(
            node_x * SNAKE_SIZE,
            node_y * SNAKE_SIZE,
            (node_x + 1) * SNAKE_SIZE,
            (node_y + 1) * SNAKE_SIZE,
            fill=snake.color,
            tag="snake"
        )


canvas.bind_all("<Key>", lambda key_pressed: snake.set_new_direction(key_pressed.keysym))


def move_snake():
    snake.move()
    draw_snake()


def game_flow():
    if snake.check_collision():
        return
    if snake.eat(food):
        spawn_food()
        score.config(text=f"Score: {snake.size - 3}")
    move_snake()
    canvas.after(GAME_SPEED, game_flow)


food = None


def spawn_food():
    global canvas
    global food
    canvas.delete("food")

    food_x = random.randint(0, GAME_WIDTH // SNAKE_SIZE - 1)
    food_y = random.randint(0, GAME_HEIGHT // SNAKE_SIZE - 1)

    while (food_x, food_y) in snake.body:
        food_x = random.randint(0, GAME_WIDTH // SNAKE_SIZE - 1)
        food_y = random.randint(0, GAME_HEIGHT // SNAKE_SIZE - 1)

    food = Food("White", food_x, food_y)

    canvas.create_rectangle(
        food_x * SNAKE_SIZE,
        food_y * SNAKE_SIZE,
        (food_x + 1) * SNAKE_SIZE,
        (food_y + 1) * SNAKE_SIZE,
        fill=food.color,
        tag="food"
    )


# Textfield
score = tkinter.Label(root, text=f"Score: {snake.size - 3}", bd=4, font="Times")

spawn_food()
score.pack()
canvas.pack()
canvas.after(GAME_SPEED, game_flow)
root.mainloop()