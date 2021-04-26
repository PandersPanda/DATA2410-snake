import grpc
import snake_pb2_grpc
from snake_pb2 import Snake, Point
from concurrent import futures


class SnakeGame(snake_pb2_grpc.SnakeServiceServicer):
    SNAKES = {}
    AVAILABLE_COLORS = ['Blue', 'Red']

    def addSnake(self, request, context):
        snake = Snake(
            color='Red',
            direction='Right',
            body=[Point(x=2, y=0), Point(x=1, y=0), Point(x=0, y=0)]
        )
        self.SNAKES.update({snake.color: snake})
        return snake

    def moveSnake(self, request, context):
        # MoveRequest(color= ... , direction=...)
        new_direction = request.direction
        snake = self.SNAKES.get(request.color, None)
        opposite_direction = [{'Up', 'Down'}, {'Left', 'Right'}]
        if {snake.direction, new_direction} in opposite_direction:
            new_direction = snake.direction
        # [Point(x=2, y=0), Point(x=1, y=0), Point(x=0, y=0)]
        new_head = Point(x=snake.body[0].x, y=snake.body[0].y)

        if new_direction == "Right":
            new_head.x += 1
        elif new_direction == "Left":
            new_head.x -= 1
        elif new_direction == "Down":
            new_head.y += 1
        elif new_direction == "Up":
            new_head.y -= 1

        snake.body.pop()
        snake.body.insert(0, new_head)
        snake.direction = new_direction

        return snake

    def getSnakes(self, request, context):
        for snake in self.SNAKES.values():
            yield snake


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    snake_pb2_grpc.add_SnakeServiceServicer_to_server(
        SnakeGame(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
