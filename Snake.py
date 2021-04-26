class Snake:
    def __init__(self, color):
        self.color = color
        self.size = 3

        # body[0] er head, being[-1] er tail
        self.body = [(2, 0), (1, 0), (0, 0)]  # x,y
        self.direction = "Right"

    def move(self):
        head_x_position, head_y_position = self.body[0]
        new_position = None

        if self.direction == "Right":
            new_position = (head_x_position + 1, head_y_position)
        if self.direction == "Left":
            new_position = (head_x_position - 1, head_y_position)
        if self.direction == "Down":
            new_position = (head_x_position, head_y_position + 1)
        if self.direction == "Up":
            new_position = (head_x_position, head_y_position - 1)

        self.body = [new_position] + self.body[:-1]
        return new_position

    def check_collision(self):
        head_x, head_y = self.body[0]

        # Check border:
        if head_x in (-1, 30) or head_y in (-1, 31) or (head_x, head_y) in self.body[1:]:
            print("Stopped moving")
            return True

    def set_new_direction(self, new_direction):
        opposite_direction = [{'Up', 'Down'}, {'Right', 'Left'}]
        if {new_direction, self.direction} not in opposite_direction:
            self.direction = new_direction

    def eat(self, food):
        if self.body[0] == food.position:
            self.body.insert(0, food.position)
            self.size += 1
            return True
        return False


class Food:
    def __init__(self, color, x, y):
        self.color = color
        self.position = (x, y)
