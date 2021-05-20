import tkinter
import grpc
import snake_pb2
import snake_pb2_grpc
import sys
import threading
import random
import time

root = tkinter.Tk()
game_canvas = None
score_window = None
host = 'localhost'
hostname = 'snakenet'
port = 50051

GAME_CONFIGURATION = snake_pb2.GameConfig()
stub = None
snake = snake_pb2.Snake()
direction = None


def show_high_scores():
    high_score_window = tkinter.Tk()
    high_score_window.geometry(f'{GAME_CONFIGURATION.window_width}x{GAME_CONFIGURATION.window_height}')
    high_score_window.resizable(False, False)
    high_score_window.title("Snake Game: Highscores")

    back_button = tkinter.Button(high_score_window, width=10, height=1, bg="red", activebackground="#cf0000",
                                 font=("bold", 20),
                                 command=high_score_window.destroy, text="Back", bd=3)

    back_button.place(x=450, y=0)

    high_score_list = tkinter.Listbox(high_score_window, height=15, width=25,
                                      font="bold")
    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    high_scores = stub.GetHighScores(snake_pb2.GetRequest())
    for i, score in enumerate(high_scores.scores):
        high_score_list.insert(i, f" {i + 1}. {score.name}: {score.score} points")

    high_score_list.place(x=175, y=200)


def show_help():
    help_window = tkinter.Tk()
    help_window.geometry(f'{GAME_CONFIGURATION.window_width}x{GAME_CONFIGURATION.window_height}')
    help_window.resizable(False, False)
    help_window.title("Snake Game: Help")

    back_button = tkinter.Button(help_window, width=10, height=1, bg="red", activebackground="#cf0000",
                                 font=("bold", 20),
                                 command=help_window.destroy, text="Back", bd=3)

    title1 = tkinter.Label(help_window, text=f"Gameplay:", font=("bold", 20))

    information_label = tkinter.Label(help_window, text=f"Snake is a game where you get bigger by eating food,\n"
                                                        "The goal is to get as big as possible, can you beat the "
                                                        "highscore?\n "
                                                        "You will die if you either hit one of the borders or crash "
                                                        "into\n "
                                                        "the other snakes", font=12)

    title2 = tkinter.Label(help_window, text=f"Controls:", font=("bold", 20))

    control_label = tkinter.Label(help_window, text=f"You move with your arrow keys or w a s d", font=20)

    back_button.place(x=450, y=0)
    title1.place(x=0, y=0)
    information_label.place(x=0, y=80)
    title2.place(x=0, y=200)
    control_label.place(x=0, y=250)


def scroll_lock_movement():
    global snake
    head = snake.body[0]
    x, y = head.x, head.y
    assert isinstance(game_canvas, tkinter.Canvas)
    game_canvas.xview_moveto(
        x * GAME_CONFIGURATION.scroll_fraction_x - GAME_CONFIGURATION.scroll_response_x
    )
    game_canvas.yview_moveto(
        y * GAME_CONFIGURATION.scroll_fraction_y - GAME_CONFIGURATION.scroll_response_y
    )


def move_snake():
    global snake
    global direction
    global stub

    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    snake = stub.MoveSnake(snake_pb2.MoveRequest(name=snake.name, direction=direction))
    scroll_lock_movement()


def draw_game_board():
    assert isinstance(game_canvas, tkinter.Canvas)
    # Draw border:
    game_canvas.create_rectangle(
        0, 0, GAME_CONFIGURATION.board_width + 1.5, GAME_CONFIGURATION.board_height + 1.5,
        fill='', outline=GAME_CONFIGURATION.border_color, width=2 * GAME_CONFIGURATION.snake_size)


def draw_segment(s):
    assert isinstance(game_canvas, tkinter.Canvas)
    game_canvas.create_rectangle(
        s.point.x * GAME_CONFIGURATION.snake_size,
        s.point.y * GAME_CONFIGURATION.snake_size,
        (s.point.x + 1) * GAME_CONFIGURATION.snake_size,
        (s.point.y + 1) * GAME_CONFIGURATION.snake_size,
        fill=s.color,
        tag='snake'
    )


def draw_all_snakes():
    global stub
    global snake
    global game_canvas

    assert isinstance(game_canvas, tkinter.Canvas)
    game_canvas.delete('snake')

    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    snake_segments = stub.GetAllSnakes(snake.body[0])
    for s in snake_segments:
        draw_segment(s)


def replay(tkinter_objects):
    global snake
    global direction
    for o in tkinter_objects:
        o.destroy()
    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    snake = stub.JoinGame(snake_pb2.JoinRequest(name=snake.name))
    direction = snake.direction
    start_game()


def game_over():
    root.geometry(f'{GAME_CONFIGURATION.window_width}x{GAME_CONFIGURATION.window_height}')

    assert isinstance(game_canvas, tkinter.Canvas)
    game_canvas.grid_forget()

    game_over_lb = tkinter.Label(root, text="Game Over", font=("Bold", 35))
    game_over_lb.place(x=200, y=200)

    score_lb = tkinter.Label(root, text=f"Your final score is {len(snake.body) - 3} points.")
    score_lb.place(x=200, y=260)

    replay_button = tkinter.Button(root, text="Play again", width=10, height=1, bg="red", activebackground="#cf0000",
                                   font=("bold", 20),
                                   command=lambda: replay([game_over_lb, score_lb, replay_button, quit_button]),
                                   bd=3)
    replay_button.place(x=220, y=300)

    quit_button = tkinter.Button(root, text="Quit", width=10, height=1, bg="red", activebackground="#cf0000",
                                 font=("bold", 20),
                                 command=root.quit,
                                 bd=3)
    quit_button.place(x=220, y=370)


def check_collision():
    global snake
    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    collision = stub.CheckCollision(
        snake_pb2.CollisionRequest(name=snake.name)
    )
    if collision.has_collided:
        stub.KillSnake(snake_pb2.KillSnakeRequest(name=snake.name))
        print(f"You died, final score for: {len(snake.body) - 3}")
        game_over()

    return collision.has_collided


def update_player_scores():
    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    scores = stub.GetCurrentPlayerScores(snake_pb2.GetRequest())

    assert isinstance(score_window, tkinter.Listbox)
    score_window.delete(1, 'end')

    for i, score in enumerate(scores.scores):
        score_window.insert(i + 1, f' {i + 1}. {score.name}: {score.score} points')
        score_window.itemconfig(i + 1, foreground=score.color)


def draw_foods():
    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    assert isinstance(game_canvas, tkinter.Canvas)

    game_canvas.delete('food')
    foods = stub.GetFood(snake.body[0])
    for f in foods:
        game_canvas.create_oval(
            (f.x + .75) * GAME_CONFIGURATION.snake_size,
            (f.y + .75) * GAME_CONFIGURATION.snake_size,
            (f.x + .25) * GAME_CONFIGURATION.snake_size,
            (f.y + .25) * GAME_CONFIGURATION.snake_size,
            fill='white',
            tag='food'
        )
    game_canvas.tag_lower('food')


def game_flow():
    global GAME_CONFIGURATION
    global stub

    move_snake()
    if check_collision():
        return
    draw_all_snakes()
    draw_foods()
    update_player_scores()
    assert isinstance(game_canvas, tkinter.Canvas)
    game_canvas.after(GAME_CONFIGURATION.game_speed, game_flow)


def change_snake_direction(event):
    global direction
    global snake
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


def random_food():
    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    while True:
        stub.AddMoreFood(snake_pb2.GetRequest())
        time.sleep(random.randint(1, 2))


def start_game():
    global game_canvas
    global score_window
    global GAME_CONFIGURATION

    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)

    root.geometry(f'{GAME_CONFIGURATION.window_width + 200}x{GAME_CONFIGURATION.window_height}')

    score_window = tkinter.Listbox(
        width=150,
        height=GAME_CONFIGURATION.window_height,
        background=GAME_CONFIGURATION.background_color,
        font="Helvetica",
    )
    score_window.place(x=GAME_CONFIGURATION.window_width, y=0)
    score_window.insert(0, " Scores:")
    score_window.itemconfig(0, foreground='white')

    game_canvas = tkinter.Canvas(
        width=GAME_CONFIGURATION.window_width,
        height=GAME_CONFIGURATION.window_height,
        highlightthickness=0,
        background=GAME_CONFIGURATION.background_color
    )
    game_canvas.config(
        scrollregion=[0, 0, GAME_CONFIGURATION.board_width, GAME_CONFIGURATION.board_height]
    )
    game_canvas.grid(row=0, column=0)
    game_canvas.bind_all('<Key>', change_snake_direction)

    draw_game_board()

    random_food_thread = threading.Thread(target=random_food, daemon=True)
    random_food_thread.start()

    game_flow()


def submit_name(username, tkinter_objects):
    global stub
    global snake
    global direction

    if username == "":
        tkinter_objects[0].configure(text="Please enter a username")
        tkinter_objects[0].place(x=220, y=222)
        return
    if len(username) > 15:
        tkinter_objects[0].configure(text="Enter a username that is under 15 characters")
        tkinter_objects[0].place(x=220, y=222)
        return

    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    try:
        snake = stub.JoinGame(snake_pb2.JoinRequest(name=username))  # Returns a snake
        direction = snake.direction
    except grpc.RpcError:
        sys.exit('This room is full of snakes!')

    for o in tkinter_objects:
        o.destroy()

    start_game()


def establish_stub():
    global stub
    with open('crt.pem', 'rb') as f:
        trusted_certs = f.read()
    credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
    channel = grpc.secure_channel(
        f'{host}:{port}',
        credentials,
        options=(('grpc.ssl_target_name_override', hostname),)
    )

    stub = snake_pb2_grpc.SnakeServiceStub(channel)


def on_closing():
    global snake
    global stub
    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    try:
        stub.KillSnake(snake_pb2.KillSnakeRequest(name=snake.name))
    except grpc.RpcError:
        pass
    root.quit()


def main():
    # Get the determined game configurations from the server
    global GAME_CONFIGURATION
    establish_stub()  # Establish stub, own function for later modifications if necessary
    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    try:
        GAME_CONFIGURATION = stub.GetGameConfigurations(snake_pb2.GetRequest())
    except grpc.RpcError as e:
        print(e)
        sys.exit(f'Cannot establish communication with server at {host}:{port}')

    # Set root window size and disable resizing
    root.geometry(f'{GAME_CONFIGURATION.window_width}x{GAME_CONFIGURATION.window_height}')
    root.resizable(False, False)
    root.title('Snake Game')

    # Index page:
    username_var = tkinter.StringVar()
    bg = tkinter.PhotoImage(file="snake.png")
    label1 = tkinter.Label(root, image=bg)
    label1.place(x=0, y=100)

    username_var = tkinter.StringVar()

    title_label = tkinter.Label(root, text='Username:', font=("bold", 20))
    message_label = tkinter.Label(text='', font=("cursive", 11))
    user_name_input = tkinter.Entry(textvariable=username_var, font=('calibre', 20))
    submit_button = tkinter.Button(
        width=10, height=1, bg="red", activebackground="#cf0000", font=("bold", 20),
        command=lambda:
        submit_name(
            username_var.get(),
            [message_label,
             user_name_input,
             submit_button,
             title_label,
             high_score_button,
             help_button]
        ),
        text="Play Game", bd=3)
    help_button = tkinter.Button(width=10, height=1, bg="red", activebackground="#cf0000", font=("bold", 20),
                                 command=show_help, text="Help", bd=3)
    high_score_button = tkinter.Button(width=10, height=1, bg="red", activebackground="#cf0000", font=("bold", 20),
                                       command=show_high_scores, text="High scores", bd=3)

    title_label.place(x=160, y=180)
    user_name_input.place(x=160, y=250)
    submit_button.place(x=220, y=300)
    help_button.place(x=220, y=380)
    high_score_button.place(x=220, y=460)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    # Run mainloop
    root.mainloop()


if __name__ == '__main__':
    main()
