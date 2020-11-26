from socket import socket
from MyCryptograpy.XChaCha20Py import XChaCha20Crypto
from MyCryptograpy.DiffieHellman import DiffieHellmanListening
import json
import Database
import struct

class Connection:

    def __init__(self):
        server_socket = socket() #create server socket to listen new connection
        server_socket.bind(('0.0.0.0',50000))
        server_socket.listen(1)
        s, addr = server_socket.accept()
        print("Connection accepted")  #client is connected, go to authentication
        server_socket.close()

        self.s = s
        diffieHellmanListening = DiffieHellmanListening(addr)
        shared_key = diffieHellmanListening.key_exchange()
        print(shared_key)
        self.crypto = XChaCha20Crypto(shared_key) #exchange a key for encrypted comunication

        user_data_json = self.receive_decrypted() #now user send json with username and password
        print("Recevied json: %s" % user_data_json)
        user_data = json.loads(user_data_json) #parse json into dict
        user_id = Database.login(user_data['username'],user_data['password'])  #if username is not in db the server will create a new account

        if user_id is None: #wrong password or error
            print("Cannot connect due to errors, closing connection..")
            self.send_encrypted('no')
            self.s.close()
            #self.successfully_connected = False
            return
        else:
            self.user_id = user_id
            self.send_encrypted(str(self.user_id))
            self.receive_decrypted() #wait for client
            self.send_all_notes()


    def is_alive(self):
        #TODO Implement this
        return True

    def receive_decrypted(self):
        s = self.s.recv(4096).decode('utf-8')
        decrypted = self.crypto.decrypt(s)
        return decrypted

    def send_all_notes(self):
        notes = Database.get_notes_from_userid(self.user_id)
        for json_note in notes:
            #jsonmsg = json.dumps(json_note)
            self.send_encrypted(json_note)
            print("Note sent: %s" % (json_note))
            self.receive_decrypted() #wait for client input
        self.send_encrypted("/end/")
        self.receive_decrypted()
        

    def send_encrypted(self,string: str):
        encryted_message = self.crypto.encrypt(string)
        self.s.send(encryted_message.encode('utf-8'))