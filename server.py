import snake_pb2
import snake_pb2_grpc
import grpc
from concurrent import futures


class SnakeGame(snake_pb2_grpc.SnakeGameServiceServicer):
    SNAKES = {}

    def addSnake(self, request, context):
        self.SNAKES.update({request.name: request})
        return request

    def locateOtherSnakes(self, request, context):
        for snake in self.SNAKES:
            if request != snake:
                yield snake

    def spawnFood(self, request, context):
        return snake_pb2.Food(color='white', position=request)

    def moveSnake(self, request, context):
        snake = self.SNAKES.get(request.name, None)
        opposite_direction = [{'Up', 'Down'}, {'Right', 'Left'}]

        if {snake.direction, request.direction} in opposite_direction:
            return snake

        head_x_position = snake.body[0].x
        head_y_position = snake.body[0].y

        if request.direction == "Right":
            new_position = snake_pb2.Point(x=head_x_position + 1, y=head_y_position)
            snake.body.insert(0, new_position)
        if request.direction == "Left":
            new_position = snake_pb2.Point(x=head_x_position - 1, y=head_y_position)
            snake.body.insert(0, new_position)
        if request.direction == "Down":
            new_position = snake_pb2.Point(x=head_x_position, y=head_y_position + 1)
            snake.body.insert(0, new_position)
        if request.direction == "Up":
            new_position = snake_pb2.Point(x=head_x_position, y=head_y_position - 1)
            snake.body.insert(0, new_position)

        snake.body.pop()
        snake.direction = request.direction
        return snake

    def eatFood(self, request, context):
        self.SNAKES.update({request.name: request})
        return request


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    snake_pb2_grpc.add_SnakeGameServiceServicer_to_server(
        SnakeGame(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
