from Connection import Connection
import Messages

class MessageChecker:

    def __init__(self,message: str,connection: Connection):
        self.message = message
        self.connection = connection


    def handle_message(self):
        if self.message == Messages.CLOSE_CONNECTION():
            self.connection.close()
            return True
        return False