import tkinter
import grpc
import snake_pb2
import snake_pb2_grpc
import sys

root = tkinter.Tk()
game_canvas = None
score_window = None
host = 'localhost'
port = 50051

GAME_CONFIGURATION = snake_pb2.GameConfig()
stub = None
snake = snake_pb2.Snake()
direction = None


def show_high_scores():
    pass


def show_help():
    pass


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


def game_over():
    root.geometry(f'{GAME_CONFIGURATION.window_width}x{GAME_CONFIGURATION.window_height}')

    assert isinstance(game_canvas, tkinter.Canvas)
    game_canvas.grid_forget()

    game_over_lb = tkinter.Label(root, text="Game Over", font=("Bold", 35))
    game_over_lb.place(x=200, y=200)

    score_lb = tkinter.Label(root, text=f"Your score was {len(snake.body) - 3}")
    score_lb.place(x=200, y=260)

    replay_button = tkinter.Button(root, text="Play again", width=10, height=1, bg="red", activebackground="#cf0000",
                                   font=("bold", 20),
                                   command=lambda: replay(gameover_lb, score_lb, replay_button, quit_button),
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


def game_flow():
    global GAME_CONFIGURATION
    global stub

    move_snake()
    if check_collision():
        return
    draw_all_snakes()

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

    game_canvas = tkinter.Canvas(
        width=GAME_CONFIGURATION.window_width,
        height=GAME_CONFIGURATION.window_height,
        highlightthickness=0,
        background=GAME_CONFIGURATION.background_color
    )
    game_canvas.config(
        scrollregion=[0, 0, GAME_CONFIGURATION.board_width, GAME_CONFIGURATION.board_height]
    )
    game_canvas.create_rectangle(
        0, 0, GAME_CONFIGURATION.board_width + 1.5, GAME_CONFIGURATION.board_height + 1.5,
        fill='', outline=GAME_CONFIGURATION.border_color, width=2 * GAME_CONFIGURATION.snake_size)
    game_canvas.grid(row=0, column=0)
    game_canvas.bind_all('<Key>', change_snake_direction)

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
    channel = grpc.insecure_channel(f'{host}:{port}')
    stub = snake_pb2_grpc.SnakeServiceStub(channel)


def main():
    # Get the determined game configurations from the server
    global GAME_CONFIGURATION
    establish_stub()  # Establish stub, own function for later modifications if necessary
    assert isinstance(stub, snake_pb2_grpc.SnakeServiceStub)
    try:
        GAME_CONFIGURATION = stub.GetGameConfigurations(snake_pb2.GetRequest())
    except grpc.RpcError:
        sys.exit(f'Cannot establish communication with server at {host}:{port}')

    # Set root window size and disable resizing
    root.geometry(f'{GAME_CONFIGURATION.window_width}x{GAME_CONFIGURATION.window_height}')
    root.resizable(False, False)
    root.title('Snake Game')

    # Index page:
    username_var = tkinter.StringVar()
    bg = tkinter.PhotoImage(file="bg.png")
    label1 = tkinter.Label(root, image=bg)
    label1.place(x=0, y=0)

    username_var = tkinter.StringVar()

    title_label = tkinter.Label(root, text='Username:', font=("bold", 20), bg="#54b9f0")
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

    # Run mainloop
    root.mainloop()


if __name__ == '__main__':
    main()