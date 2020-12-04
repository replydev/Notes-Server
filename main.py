from Config import Config
from MessageChecker import MessageChecker
from Connection import Connection
from threading import Thread
import Database
import argon2
import json

def main():
    config = Config('config.json')
    Database.connect(config)
    Database.check_tables()
    threads = []
    while True:
        connection = Connection()
        threads.append(Thread(target=handleConnection,args=(connection,)))
        threads[len(threads) - 1].start() # TODO Terminated threads are still in this list, clear memory

def handleConnection(connection: Connection):
    while connection.is_alive():
        message_from_client = connection.receive_decrypted() #wait for user message
        if message_from_client == '':
            message_from_client = 'CLOSE_CONNECTION'
        message_checker = MessageChecker(message_from_client,connection)
        #correctly handled message
        if message_checker.handle_message(): 
            continue

        note_dict = json.loads(message_from_client)
        note_id = note_dict['id'] = Database.get_new_free_id()
        author_id = note_dict['author']
        Database.add_note(message_from_client,note_id,author_id)
        connection.send_encrypted("ok")
    print("Connection closed by user")
        


if __name__ == '__main__':
    main()