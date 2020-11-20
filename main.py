from Config import Config
from Connection import Connection
import Database
import argon2

def main():
    config = Config('config.json')
    Database.connect(config)
    Database.check_tables()

    connection = Connection()
    Database.close()


if __name__ == '__main__':
    main()