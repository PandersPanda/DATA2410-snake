import mysql.connector

config = {
    'user': 'app_user',
    'password': 'k2znHSJnNlmi5znh',
    'host': '35.228.86.138',
}

name = 'thanos'
cnxn = mysql.connector.connect(**config)
cursor = cnxn.cursor()

cursor.execute("USE snake_highscores")
cursor.execute(
    f"SELECT username, score FROM highscores "
    f"WHERE username = '{name}'"
)
out = cursor.fetchall()
cursor.close()
cnxn.close()

print(out)


