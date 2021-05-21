# DATA2410 Spring 2021 Portfolio 2

DATA2410 - Networking and Cloud services is a subject taught at Oslo Metropolitan University. This project is one of
two projects included in the final grade for the subject. Portfolio 2 is about creating a service with a backend
that should communicate with a frontend. Furthermore, deploying the service with Docker was one of the requirements 
for this project. Students were supposed to work in teams to develop a solution to the given task. For this project
each team were supposed to choose one of two tasks to solve.

###### Our team:

- Andreas Torres Hansen (s338851) [GitHub](https://github.com/AndreasTHansen)
- Anders Hagen Ottersland (s341883) [GitHub](https://github.com/PandersPanda)
- Uy Quoc Nguyen (s341864) [GitHub](https://github.com/uyqn)

Our implementation of this portfolio can also be found on [GitHub](https://github.com/PandersPanda/Data2410-snake.git).

---

## Task 2: A multiplayer game
###### The task description:
> The task is to implement the classic [Snake](https://en.wikipedia.org/wiki/Snake_(video_game_genre)) , as a 
> multiplayer game. Anything from a very simple game with a small screen and two players is allowed. You are allowed to 
> implement another game instead, but ask first.

The reason that this task was chosen was because all of us are gaming enthusiasts. Furthermore, Task 1 was to implement
a web shop with a REST API server, similar to a previous assignment we had to solve. Thus, we chose this task to
challenge ourselves and to cease the opportunity to learn new technologies.
---

### How to run our implementation:
The easiest way to start playing is to first start the server by entering the following command from the source folder:
````commandline
docker-compose up
````
This will also start [Prometheus](https://prometheus.io/) at localhost:9090 which you can use to monitor the network 
traffic. Then, when all of the containers are up and running you can start the game with the following command:
````commandline
python3 client.py
````
---
However, if monitoring the network traffic is not a priority you can also just start the server container with first 
building with
````commandline
docker build -t snake-service .
````
Then start the server container with
````commandline
docker run -p 50051:50051 snake-service
````
From here enter
````commandline
python3 client.py
````
to start the game. In addition, if one wishes to watch a bot play you can start the game with
````commandline
python3 client.py --bot
````

---

### Technology choices
From a list of recommended technologies to choose from our team decided upon the following technologies to implement 
the solution: **Python 3** with **tkinter** for graphics and **gRPC** for networking. We chose these technologies
because it was from the provided recommended list, thus making sure that we did not use any technologies that were to be
deemed unacceptable. Furthermore, all of us has been using Python to solve previous assignments.

---
### User stories
For this project we were also provided some user stories to be fulfilled:
- [x] I can start the program, and I easily get to start playing alone even if no other players are connected.
  > Just enter a username you want to play as and hit the "Play Game" button to start the game.
    
- [x] I can move the snake around the board using the keyboard to avoid obstacles (walls or players) or steer towards 
  rewards (e.g. food - optionally dead players can turn into food).
  > Use the keyboard arrow keys or wasd to move the snake around. When a snake dies one of its segments becomes food
  > for other players. The snake will produce 1 food per 3 segments of its body. Every snake starts with a length of 3
  - [x] The game tells me which keys to use so that I don't have to refer to the documentation.
    > There is a "Help" button at the start of the game that will give you an overview of how the game works.
- [x] If I run into walls (if there are any) or other players it will kill me. If other players run into me it will 
  kill them. 
  > We made the board very big to account for a lot of players. We also added a border so running into the border will
  > kill the snake. In addition, if another snake runs into another player it will kill them and produce food.
  - [x] I clearly see an indication that I've died if I run into another player or a wall.
    > When you die you will be taken out of the game to the game over screen. From here you be provided with your final
    > score. Also, you can rejoin the game with the "Play again" button or quit the game with "Quit".
  - [x] If there are no outer walls in the game (e.g. like slither.io) will scroll with the direction of my snake when 
    I move it.
    > We did in fact implement a wall however, taken into consideration for the big size of the game board we made the
    > camera scroll with the snake.
- [x] I can clearly see if other players connect (including bots if any), in a list of connected users. 
  A minimum of 2 players must be supported.
  > To the right of the game there is a list of connected players matching the color of their snake together with their 
  > current score relative to all the other connected players. It has also been tested that a minimum of 2 players can
  > play on the same board against each other at the same time.
  - [x] There may be other players operated by the software (e.g. return of the bots - as snakes!) but this is not a 
    requirement. If there are bots they behave like any other player, and I won't be able to tell the difference 
    (except maybe if they play really badly or superhumanly well)
    > There is an attempt to add bots to the to the game. However, they are not very smart and often run into
    > themselves if they get too long. This is because no optimal path algorithm has been implemented and just a simple
    > calculation to avoid collision is added to the intelligence of the bot. It also, uses random movement when there
    > are more options available.
- [x] I can get the snake to grow by running into "food". The food can be just colored squares but I can see that 
  they're different from walls if there are any.
  > Each food will grow the snake by one size, and also provide 1 point towards your final score. Since, the snake are
  > colored square, we made the food to white colored dots instead.
- [x] I get points for getting a bigger snake and I can see how many points I have. 
  > Each time your snake runs into food you get bigger which also gives you 1 additional point towards your final
  > score. Your current score is displayed beside your name of the list of the connected players to the right of the 
  > game
---
### Requirements and implementation options 
- [x] A minimum of 2 players must be supported
> We have tested playing with 2 players and know that the game is supported.
- [ ] You can implement more games than one if you want. You can also choose another game, but make sure to ask the 
  teacher for advice if you do.
> Due to time constraints and that some of us has enrolled into extra courses this year, consequently had to focus on
> exams for the additional courses we chose to just focus on the one suggested game (snake).
---
### Deployment with Docker
> There must be a dockerfile for the server that allows you to start a game server using docker build / docker run 
> commands. It should then be possible to deploy your game server in a public cloud making it available for players 
> across the internet. 

The source folder includes a Dockerfile that can be built with
````commandline
docker build -t name:tag .
````
which can be run with
````commandline
docker run -p 50051:50051 name
````
Furthermore, it also includes a docker-compose.yml file which can be built and ran with
````commandline
docker-compose up
````
to run the server container for the game in conjunction with Prometheus and cAdvisor for network monitoring.

---

### Stretch goals
We were also provided with a non-required list of goals to aim for. Since we were only developing one game for
this task we tried to aim for as many of them as possible after we were done with the required goals.
- [x] Secure all communication with TLS. Look at https://www.grpc.io/docs/guides/auth/#examples for examples in many 
  languages. 
  > We were able to secure communication between client and server with TLS by using [openssl](https://www.openssl.org/)
  > With the command
  > ````commandline
  > openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out crt.pem -subj /CN=snakenet
  > ````
  > we received a key and certificate which we passed onto the client and server by following the provided 
  > [example](https://www.grpc.io/docs/guides/auth/#examples). However, this posed a problem as we found out that since
  > the common name was provided as "snakenet" we somehow have to override the target name to the server. We overcame 
  > this by adding the following key to the `grpc.secure_channel()` in python:
  >````python
  >host = 'localhost'
  >hostname = 'snakenet'
  >port = 50051
  >channel = grpc.secure_channel(
  >      f'{host}:{port}',
  >      credentials,
  >      options=(('grpc.ssl_target_name_override', hostname),)
  >)
  >````
  
- [x] Add monitoring using Prometheus to track the resource usage of your game server. Document how the resource usage 
  changes when many players are connected.
  > We have included Prometheus and cAdvisor as services under docker containers.
  > ````commandline
  > docker-compose up
  > ````
  > Will start a Prometheus and cAdvisor container together with the game server. From here one can go to 
  > localhost:9090 to track the resource usage. Under the "graph" section one can use the queries provided by cAdvisor. 
  > The documentation for cAdvisor can be found 
  > **[here](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md)**. It is also possible to track 
  > the resource usage of the game server by going directly to cAdvisor at http://localhost:8080/docker/snake-service. 
  > 
- [x] Allow for many (>10) or unlimited players. This will require you to manage a large grid and you probably have to
  make the game board itself scroll around the snake than to make the snakes move around the game board. 
  > The game board is set to be 16 times as large as the window that you will see to account for many players. The food
  > is also randomly generated ever 1 to 2 seconds, so the game board does not become a bare wasteland. In addition,
  > the server always ensures that there is at least 1 food on the game board at all times.
- [x] Add bots. This is a good way to test the scalability of your service by pushing it to the limit. 
  > Bots has been implemented into the game. Start a bot with
  > ````commandline
  > python3 client.py --bot
  >````
  > They are however, not very smart and tends to die pretty fast if they achieve some length. A simple check to choose
  > a new direction if it can anticipate collision is added but more than not it will just choose a random direction if
  > it thinks it will collide and trap itself.
- [x] Add a persistent high-score list with a database backend. Note that high-score lists can be fairly hard to keep 
  from being hacked (I've tried!). Some intelligent notes on why that is, and a possible solution would be an 
  interesting read.
  > A database has been added to the server side of the code to keep track of the scores. The database was created in
  > Google Cloud Platform. Thus, we chose to not run a docker container for the database. The game has implementation
  > to query the database when a snake dies. One can also view a list of high scores of players by clicking on the
  > "High scores" button at the start of the game.
  

### Some words on SQL-security

By connecting to the database in the server.py-file, some security issues arise. Most obviously,
the login-information to the database becomes visible to anyone who possesses access to the file.
We solved this by creating an extra user in the database ("app-user") with very specific rights, instead of using the
root-user. Although there is no crucial information in the database, we wanted to limit the risk of hackers accessing it
and deleting information.
