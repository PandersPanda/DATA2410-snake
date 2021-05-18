import mysql.connector

config = {
        'user': 'app_user',
        'password': 'k2znHSJnNlmi5znh',
        'host': '35.228.86.138',
}

cnxn = mysql.connector.connect(**config)

cursor = cnxn.cursor()
cursor.execute("USE snake_highscores")
cursor.execute("SELECT username, score FROM highscores "
               "WHERE username='sdojfbisdufbg'"
               "ORDER BY score DESC")
out = cursor.fetchall()

cursor.close()
cnxn.close()

print(out)