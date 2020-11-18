from socket import socket
from MyCrypto import MyCrypto
from argon2 import PasswordHasher
from pyDH import DiffieHellman
import json
import Database

class Connection:


    def key_exchange(self):
        diffie_helman = DiffieHellman()
        public_key = diffie_helman.gen_public_key()
        self.s.send(str(public_key).encode("utf-8"))
        other_client_public_key = int(self.s.recv(1024).decode("utf-8"))
        shared_key = diffie_helman.gen_shared_key(other_client_public_key)
        return shared_key

    def __init__(self,s: socket):
        server_socket = socket() #create server socket to listen new connection
        server_socket.bind(('0.0.0.0',50000))
        server_socket.listen(1)
        s, addr = server_socket.accept()
        print("Connection accepted")  #client is connected, go to authentication
        server_socket.close()

        self.s = s
        self.crypto = MyCrypto(self.key_exchange()) #exchange a key for encrypted comunication

        user_data_json = self.crypto.decrypt(s.recv(1024).decode('utf-8')) #now user send json with username and password
        user_data = json.loads(user_data_json) #parse json into dict
        user_id = Database.get_userid(user_data['username'],user_data['password'])

        if user_id is None:
            print("Cannot connect due to errors, closing connection..")
            self.s.close()
            #self.successfully_connected = False
            return
        else:
            self.user_id = user_id

    def send_all_notes(self):
        Database.get_notes_from_userid(self.user_id)
        

        

        

        







    def send(self,string: str):
        self.s.send()