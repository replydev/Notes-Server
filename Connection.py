from socket import socket
from MyCryptograpy.XChaCha20Py import XChaCha20Crypto
from MyCryptograpy.DiffieHellman import DiffieHellmanListening
import json
import Database

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

        received_json = self.receive_message() #now user send json with username and password
        print("Recevied json: %s" % received_json)

        if received_json == "":
            print("Corrupt authentication, closing the socket...")
            self.s.close()
            return

        user_data_json = self.crypto.decrypt(received_json) #decrypt
        user_data = json.loads(user_data_json) #parse json into dict
        user_id = Database.login(user_data['username'],user_data['password'])  #if username is not in db the server will create a new account

        if user_id is None: #wrong password or error
            print("Cannot connect due to errors, closing connection..")
            self.s.send('no'.encode('utf-8'))
            self.s.close()
            #self.successfully_connected = False
            return
        
        self.user_id = user_id
        self.send_all_notes()
        input("Blocking thread...")


    def receive_message(self):
        s = self.s.recv(1024).decode('utf-8')
        return s

    def send_all_notes(self):
        notes = Database.get_notes_from_userid(self.user_id)
        jsonmsg = json.dumps(notes)
        print("Sending all notes: %s" % (jsonmsg))
        self.send(jsonmsg)

    def send(self,string: str):
        encryted_message = self.crypto.encrypt(string)
        self.s.send(encryted_message.encode('utf-8'))