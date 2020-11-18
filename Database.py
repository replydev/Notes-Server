import mariadb
import sys
import FileUtils
from Config import Config

from argon2 import PasswordHasher

def connect(conf: Config ,host='localhost',port=3306):
    global conn
    try:
        conn = mariadb.connect(
            user=conf.getDatabaseUser(),
            password=conf.getDatabasePasswd(),
            host=host,
            port=port,
            database=conf.getDatabaseName())
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    finally:
        global config
        config = conf
        global argon2
        argon2 = PasswordHasher()

def close():
    global conn
    conn.close()

def check_tables():
    global conn
    global config
    cur = conn.cursor()

    users_sql = FileUtils.readFile('queries/create_users_table.sql')
    notes_sql = FileUtils.readFile('queries/create_notes_table.sql')
    associations_sql = FileUtils.readFile('queries/create_associations_table.sql')

    cur.execute(users_sql)
    cur.execute(notes_sql)
    cur.execute(associations_sql)
    cur.close()

def get_userid(username,password):
    global conn
    global config
    cursor = conn.cursor()
    users = []
    cursor.execute("SELECT id, username, password FROM ?.users WHERE username = ?",(config.getDatabaseName(),username))

    for (id,dbUsername,dbPassword) in cursor:
        users.append({
            'id': id,
            'username': dbUsername,
            'password': dbPassword
        })

    cursor.close()

    if len(users) == 0:
        print("User \"%s\" not found" % (username))
        return None
    elif len(users) > 1:
        print("Fatal error, there are multiple users with username \"%s\"" % (username))
        print(users)
        return None

    #now we are sure that users list contains only one user
    global argon2

    if argon2.verify(users[0]['password'],password):  # verify password insert by user comparing with the hash stored in db
        return users[0]['id']
    else:
        print("Wrong password!")
        return None

def get_notes_from_userid(userid):
    cursor = conn.cursor()
    notes = {}
    index = 0
    notes_query = FileUtils.readFile('queries/notes_query.sql')
    cursor.execute(notes_query)

    for (data) in cursor:
        notes[index] = data

    return notes