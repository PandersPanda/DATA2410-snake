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

GAME_WIDTH = 600
GAME_HEIGHT = 620

root = tkinter.Tk()
root.geometry(f'{GAME_WIDTH}x{GAME_HEIGHT}')
root.resizable(False, False)
root.title("Snake Game")

canvas = tkinter.Canvas(width=GAME_WIDTH, height=GAME_HEIGHT, highlightthickness=0, background='grey6')


channel = grpc.insecure_channel('localhost:50051')

stub = snake_pb2_grpc.SnakeServiceStub(channel)
try:
    snake = stub.addSnake(snake_pb2.JoinRequest())
except grpc.RpcError:
    print("This room is full of snakes!")
    sys.exit()
direction = snake.direction
target = snake_pb2.Point(x=-1, y=-1)


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
    assert 0 <= food.x < 30
    assert 0 <= food.y < 31

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
    snake = stub.moveSnake(
        snake_pb2.MoveRequest(color=snake.color, direction=direction)
    )


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
    has_collided = stub.checkCollision(
        snake_pb2.CollisionRequest(color=snake.color)
    )
    return has_collided.has_collided


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
        time.sleep(random.randint(2, 5))


def update_score():
    canvas.itemconfigure('score', text=f"Score: {len(snake.body) - 3}")


def game_flow():
    global snake
    move_snake()
    if check_collision():
        root.quit()
    draw_all_snakes()
    update_score()
    spawn_foods()
    canvas.after(GAME_SPEED, game_flow)


def death_move(new_direction, other_snakes):
    global snake
    head = snake_pb2.Point(x=snake.body[0].x, y=snake.body[0].y)
    if new_direction == 'Right':
        head.x = (head.x + 1) % 30
    elif new_direction == 'Left':
        head.x = (head.x - 1) % 30
    elif new_direction == 'Down':
        head.y = (head.y + 1) % 31
    elif new_direction == 'Up':
        head.y = (head.y - 1) % 31
    return head in snake.body[1:] or head in other_snakes


def avoid_collision():
    global direction
    moves = ['Up', 'Down', 'Left', 'Right']
    moves.remove(direction)
    moves.remove(opposite_direction())
    snakes = draw_all_snakes()
    snakes.remove(snake)
    other_snakes = []
    for s in snakes:
        other_snakes.extend(s.body)

    going_to_die = death_move(direction, other_snakes)
    new_direction = direction
    while going_to_die:
        if len(moves) == 0:
            break
        new_direction = random.choice(moves)
        moves.remove(new_direction)
        going_to_die = death_move(new_direction, other_snakes)

    direction = new_direction


def lock_on_to_food():
    global target
    foods = spawn_foods()
    if target not in foods:
        target = random.choice(foods)


def is_opposite_direction(new_direction):
    return {direction, new_direction} in [{'Up', 'Down'}, {'Left', 'Right'}]


def opposite_direction():
    opposite_dictionary = {
        'Up': 'Down',
        'Down': 'Up',
        'Left': 'Right',
        'Right': 'Left'
    }
    return opposite_dictionary[direction]


def get_legal_moves():
    global direction
    opposite_dir = {
        'Up': 'Down',
        'Down': 'Up',
        'Left': 'Right',
        'Right': 'Left'
    }
    legal_moves = ['Up', 'Down', 'Right', 'Left']
    opp = opposite_dir.get(direction, None)
    if opp:
        legal_moves.remove(opp)
    return legal_moves


def move_to_food():
    global target
    global direction
    global snake

    target_x = target.x - snake.body[0].x
    target_y = target.y - snake.body[0].y

    if target_x < 0:
        new_direction = 'Left'
        if is_opposite_direction(new_direction):
            new_direction = random.choice(['Up', 'Down'])
    elif target_x > 0:
        new_direction = 'Right'
        if is_opposite_direction(new_direction):
            new_direction = random.choice(['Up', 'Down'])
    elif target_y < 0:
        new_direction = 'Up'
        if is_opposite_direction(new_direction):
            new_direction = random.choice(['Left', 'Right'])
    else:
        new_direction = 'Down'
        if is_opposite_direction(new_direction):
            new_direction = random.choice(['Left', 'Right'])
    direction = new_direction
    avoid_collision()

    snake = stub.moveSnake(snake_pb2.MoveRequest(color=snake.color, direction=direction))


def bot_flow():
    lock_on_to_food()
    move_to_food()
    if check_collision():
        print(f"Your snake died, final score: {len(snake.body) - 3}")
        root.quit()
    draw_all_snakes()
    update_score()
    canvas.after(GAME_SPEED, bot_flow)


def start_game(event=None):
    start_game_button.destroy()
    multiplayer_button.destroy()
    canvas.pack()
    canvas.create_text(
        40, 15,
        text=f"Score: {len(snake.body) - 3}",
        fill=snake.color, tag='score',
        font=('TkDefaultFont', 12)
    )
    random_food_thread = threading.Thread(target=random_food, daemon=True)
    random_food_thread.start()
    canvas.bind_all('<Key>', change_direction)
    game_flow()


def on_closing():
    canvas.delete('all')
    stub.removeSnake(snake)
    root.quit()


start_game_button = tkinter.Button(root, text="Single player")
multiplayer_button = tkinter.Button(root, text="Multiplayer")
start_game_button.bind('<Button-1>', start_game)
multiplayer_button.bind('<Button-2>', start_game)
start_game_button.place(x=260, y=250)
multiplayer_button.place(x=260, y=300)
root.protocol("WM_DELETE_WINDOW", on_closing)
# start_game()
root.mainloop()
