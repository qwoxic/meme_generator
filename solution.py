import sqlite3

con = sqlite3.connect(input())
cur = con.cursor()

result = cur.execute("""
    SELECT DISTINCT(duration) 
    FROM (SELECT title, duration FROM Films 
    WHERE duration IN (45, 90))
""").fetchall()

con.close()

for item in result:
    print(item[0])
