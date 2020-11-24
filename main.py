from Config import Config
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
        threads[len(threads) - 1].start()

def handleConnection(connection: Connection):
    while connection.is_alive():
        message_from_client = connection.receive_message() #wait for user message
        decrypted_message_from_client = connection.crypto.decrypt(message_from_client)
        note_dict = json.loads(decrypted_message_from_client)
        note_id = note_dict['id']
        author_id = note_dict['author']
        Database.add_note(decrypted_message_from_client,note_id,author_id)
        connection.send_encrypted("yes")
        


if __name__ == '__main__':
    main()