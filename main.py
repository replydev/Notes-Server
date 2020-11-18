from Config import Config
import Database

def main():
    config = Config('config.json')
    Database.connect(config)
    Database.check_tables()

    print(Database.get_notes_from_userid(1))


if __name__ == '__main__':
    main()