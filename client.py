import random
import tkinter
import grpc
import snake_pb2
import snake_pb2_grpc
import time
import threading
import sys
import mysql.connector

config = {
    'user': 'app_user',
    'password': 'k2znHSJnNlmi5znh',
    'host': '35.228.86.138'
}

cnxn = mysql.connector.connect(**config)

cursor = cnxn.cursor()
cursor.execute('USE snake_highscores')
cursor.execute('CREATE TABLE IF NOT EXISTS googlegud('
               'id int(6) PRIMARY KEY'
               ') ')
cnxn.close()

SNAKE_SIZE = 20
GAME_SPEED = 50

WINDOW_WIDTH = 620
WINDOW_HEIGHT = 620

GAME_WIDTH = 4 * WINDOW_WIDTH
GAME_HEIGHT = 4 * WINDOW_WIDTH

GRID_ELEMENT_X = GAME_WIDTH // SNAKE_SIZE
GRID_ELEMENT_Y = GAME_HEIGHT // SNAKE_SIZE

SCROLL_RESPONSE_X = 1 / (2 * GAME_WIDTH / WINDOW_WIDTH)
SCROLL_FRACTION_X = 1 / GRID_ELEMENT_X

SCROLL_RESPONSE_Y = 1 / (2 * GAME_HEIGHT / WINDOW_HEIGHT)
SCROLL_FRACTION_Y = 1 / GRID_ELEMENT_Y

BACKGROUND_COLOR = 'grey6'
BORDER_COLOR = 'red4'

root = tkinter.Tk()
root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
root.resizable(False, False)
root.title("Snake Game")

bg = tkinter.PhotoImage(file="bg.png")
label1 = tkinter.Label(root, image=bg)
label1.place(x=0, y=0)

score_canvas = tkinter.Canvas(width=WINDOW_WIDTH, height=20)

channel = grpc.insecure_channel('localhost:50051')
stub = snake_pb2_grpc.SnakeServiceStub(channel)
try:
    snake = stub.addSnake(snake_pb2.JoinRequest(maxX=GRID_ELEMENT_X, maxY=GRID_ELEMENT_Y))
except grpc.RpcError:
    print("This room is full of snakes!")
    sys.exit()

direction = snake.direction

canvas = tkinter.Canvas(width=WINDOW_WIDTH, height=WINDOW_HEIGHT - 20,
                        highlightthickness=0, background=BACKGROUND_COLOR)

canvas.config(scrollregion=[0, 0, GAME_WIDTH, GAME_HEIGHT])
canvas.create_rectangle(0, 0, GAME_WIDTH + 1.5, GAME_HEIGHT + 1.5,
                        fill='', outline=BORDER_COLOR, width=2 * SNAKE_SIZE)


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


def draw_food(food, r, color):
    assert 0 < r <= 1

    food = canvas.create_oval(
        (food.x + .5 + r / 2) * SNAKE_SIZE,
        (food.y + .5 + r / 2) * SNAKE_SIZE,
        (food.x + .5 - r / 2) * SNAKE_SIZE,
        (food.y + .5 - r / 2) * SNAKE_SIZE,
        fill=color,
        tag='food'
    )
    canvas.tag_lower(food)


def move_snake():
    global snake
    global direction
    global canvas
    snake = stub.moveSnake(
        snake_pb2.MoveRequest(color=snake.color, direction=direction)
    )
    x_lock = snake.body[0].x
    y_lock = snake.body[0].y
    canvas.xview_moveto(x_lock * SCROLL_FRACTION_X - SCROLL_RESPONSE_X)
    canvas.yview_moveto(y_lock * SCROLL_FRACTION_Y - SCROLL_RESPONSE_Y)


def change_direction(event):
    global direction
    available_directions = {
        'Up': 'Up',
        'Down': 'Down',
        'Left': 'Left',
        'Right': 'Right',
        'w': 'Up',
        'a': 'Left',
        's': 'Down',
        'd': 'Right'
    }
    new_direction = available_directions.get(event.keysym, False)
    if new_direction:
        direction = new_direction


def check_collision():
    collision = stub.checkCollision(
        snake_pb2.CollisionRequest(color=snake.color)
    )
    return collision.has_collided


def draw_all_snakes():
    canvas.delete('snake')
    snakes = stub.getSnakes(snake_pb2.GetRequest())
    snake_list = []
    for s in snakes:
        draw_snake(s)
        snake_list.append(s)
    return snake_list


def spawn_foods():
    canvas.delete('food')
    foods = stub.getFood(snake_pb2.FoodRequest())
    food_list = []
    for f in foods:
        draw_food(food=f, r=0.5, color='White')
        food_list.append(f)
    return food_list


def random_food():
    while True:
        stub.addMoreFood(snake_pb2.FoodRequest())
        time.sleep(random.randint(1, 2))


def update_score():
    score_canvas.itemconfigure('score', text=f"Score: {len(snake.body) - 3}")


def game_flow():
    move_snake()
    if check_collision():
        snakes = stub.getSnakes(snake_pb2.GetRequest())
        for s in snakes:
            stub.removeSnake(s)
        print(f"You died, final score for: {len(snake.body) - 3}")
        game_over()
        return
    draw_all_snakes()
    update_score()
    spawn_foods()
    canvas.after(GAME_SPEED, game_flow)


def start_game(event=None):
    message_label.destroy()
    score_canvas.pack()
    help_button.destroy()

    canvas.pack()
    score_canvas.create_text(
        40, 15,
        text=f"Score: {len(snake.body) - 3}",
        fill=snake.color, tag='score',
        font=('TkDefaultFont', 12)
    )
    score_canvas.create_text(
        200, 15,
        text=f"Username: " + username,
        fill=snake.color, tag='username',
        font=('TkDefaultFont', 12)
    )

    random_food_thread = threading.Thread(target=random_food, daemon=True)
    random_food_thread.start()
    canvas.bind_all('<Key>', change_direction)
    game_flow()


def game_over():
    canvas.pack_forget()
    gameover_lb = tkinter.Label(root, text="Game Over", font=("Bold", 35))
    gameover_lb.place(x=200, y=200)

    score_lb = tkinter.Label(root, text=f"Your score was {len(snake.body) - 3}")
    score_lb.place(x=200, y=260)

    replay_button = tkinter.Button(root, text="Play again", width=10, height=1, bg="red", activebackground="#cf0000",
                                   font=("bold", 20),
                                   command=lambda: replay(gameover_lb, score_lb, replay_button),
                                   bd=3)
    replay_button.place(x=220, y=300)


def replay(gameover, score, button):
    global snake
    global direction
    button.destroy()
    gameover.destroy()
    score.destroy()
    snake = stub.addSnake(snake_pb2.JoinRequest(maxX=GRID_ELEMENT_X, maxY=GRID_ELEMENT_Y))
    direction = snake.direction
    start_game()


def submit():
    global username
    username = username_var.get()

    if username == "":
        message_label.configure(text="Please enter a username")
        message_label.place(x=220, y=450)
        return
    if len(username) > 15:
        message_label.configure(text="Enter a username that is under 15 characters")
        message_label.place(x=220, y=450)
        return

    user_name_input.destroy()
    submit_button.destroy()
    title_label.destroy()
    start_game()


def show_help():
    help_window = tkinter.Tk()
    help_window.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
    help_window.resizable(False, False)
    help_window.title("Snake Game: Help")

    frame1 = tkinter.Frame(help_window)
    back_button = tkinter.Button(help_window, width=10, height=1, bg="red", activebackground="#cf0000",
                                 font=("bold", 20),
                                 command=help_window.destroy, text="Back", bd=3)

    title1 = tkinter.Label(help_window, text=f"Gameplay:", font=("bold", 20))

    information_label = tkinter.Label(help_window, text=f"Snake is a game where you get bigger by eating food,\n"
                                                        "The goal is to get as big as possible, can you beat the highscore?\n"
                                                        "You will die if you either hit one of the borders or crash into\n"
                                                        "the other snakes", font=12)

    title2 = tkinter.Label(help_window, text=f"Controls:", font=("bold", 20))

    control_label = tkinter.Label(help_window, text=f"You move with your arrow keys or w a s d", font=20)

    back_button.place(x=450, y=0)
    title1.place(x=0, y=0)
    information_label.place(x=0, y=80)
    title2.place(x=0, y=200)
    control_label.place(x=0, y=250)


def on_closing():
    canvas.delete('all')
    root.quit()


title_label = tkinter.Label(root, text='Username:', font=("bold", 20), bg="#54b9f0")
message_label = tkinter.Label(text='', font=("cursive", 11))
username_var = tkinter.StringVar()
username = ""
user_name_input = tkinter.Entry(textvariable=username_var, font=('calibre', 20))
submit_button = tkinter.Button(width=10, height=1, bg="red", activebackground="#cf0000", font=("bold", 20),
                               command=submit, text="Play Game", bd=3)
help_button = tkinter.Button(width=10, height=1, bg="red", activebackground="#cf0000", font=("bold", 20),
                             command=show_help, text="Help", bd=3)

title_label.place(x=160, y=200)
user_name_input.place(x=160, y=250)
submit_button.place(x=220, y=300)
help_button.place(x=220, y=380)

root.protocol("WM_DELETE_WINDOW", on_closing)
# start_game()
root.mainloop()
