import mariadb
import sys
import FileUtils
from Config import Config
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

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

def get_user(username):
    global conn
    cursor = conn.cursor(prepared=True)
    users = []
    cursor.execute("SELECT id, username, password FROM users WHERE username = %s",(username,))

    for (id,dbUsername,dbPassword) in cursor:
        users.append({
            'id': id,
            'username': dbUsername,
            'password': dbPassword
        })

    cursor.close()
    return users

def exists(username):
    return len(get_user(username)) > 0

def get_userid(username: str,password: str):
    users = get_user(username)

    if len(users) == 0:
        print("User \"%s\" not found" % (username,))
        create_user(username,password)
        return get_userid(username,password)
    elif len(users) > 1:
        print("Fatal error, there are multiple users with username \"%s\"" % (username,))
        print(users)
        return None

    #now we are sure that users list contains only one user
    global argon2

    hashed_user_password = users[0]['password']
    hashed_user_id = users[0]['id']

    try:
        if argon2.verify(hashed_user_password,password):  # verify password insert by user comparing with the hash stored in db
            return hashed_user_id
        else:
            print("Wrong password!")
            return None
    except VerifyMismatchError:
        print("Wrong password!")
        return None

def create_user(username,password):
    global conn
    global argon2
    cursor = conn.cursor(prepared=True)
    insert_sql = FileUtils.readFile('queries/insert_user.sql')
    hashed_password = argon2.hash(password)
    cursor.execute(insert_sql,(username,hashed_password))
    print("Created new user: %s:%s" % (username,hashed_password))
    conn.commit() #commit changes
    cursor.close()

def get_notes_from_userid(userid):
    cursor = conn.cursor(prepared=True)
    notes = {}
    index = 0
    notes_query = FileUtils.readFile('queries/notes_query.sql')
    cursor.execute(notes_query,(str(userid),))

    for (data) in cursor:
        notes[index] = data

    return notes