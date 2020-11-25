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

def login(username: str,password: str):
    users = get_user(username)

    if len(users) == 0:
        print("User \"%s\" not found" % (username,))
        create_user(username,password)
        return login(username,password)
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
            if argon2.check_needs_rehash(hashed_user_password):
                set_password_for_user(id,argon2.hash(password))
            print("User authenticated!")
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
    notes = []
    notes_query = FileUtils.readFile('queries/notes_query.sql')
    cursor.execute(notes_query,(str(userid),))

    for data in cursor:
        notes.append(data[0])

    return notes


def set_password_for_user(id,new_hash):
    cursor = conn.cursor(prepared=True)
    update_passw_sql = FileUtils.readFile('queries/update_user_password.sql')
    cursor.execute(update_passw_sql,(id,new_hash))
    conn.commit()
    cursor.close()


def get_note(id):
    global conn
    cursor = conn.cursor(prepared=True)
    notes = []
    cursor.execute("SELECT id FROM notes WHERE id = %s",(id,))

    for (id) in cursor:
        notes.append({
            'id': id
            })

    cursor.close()
    return notes


def note_exist(id):
    return len(get_note(id)) > 0


def add_note(encrypted_note_json,note_id,author_id):
    global conn
    cursor = conn.cursor(prepared=True)
    if note_exist(note_id):
        update_existing_note_sql = FileUtils.readFile('queries/update_existing_note.sql')
        cursor.execute(update_existing_note_sql,(note_id,encrypted_note_json))
    else:
        insert_note_sql = FileUtils.readFile('queries/insert_note.sql')
        insert_association_sql = FileUtils.readFile('queries/insert_association.sql')
        cursor.execute(insert_note_sql,(note_id,encrypted_note_json))
        conn.commit()
        cursor.close()
        cursor = conn.cursor()
        cursor.execute(insert_association_sql,('',author_id,note_id))

    conn.commit()
    cursor.close()
