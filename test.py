import mysql.connector

config = {
    'user': 'root',
    'password': 'bEffFzkfGD4l3m8h',
    'host': '35.228.86.138',
}

name = 'uyqn'
cnxn = mysql.connector.connect(**config)
cursor = cnxn.cursor()

cursor.execute("USE snake_highscores")
cursor.execute(
    f"SELECT * FROM highscores"
)
out = cursor.fetchall()
cursor.close()
cnxn.close()
print(out)


