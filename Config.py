import json

class Config:

    def __init__(self,filename):
        file = open(filename,'r')
        jsons = file.read()
        self.settings = json.loads(jsons)
        file.close()

    def getDatabaseName(self):
        return self.settings['database_name']

    def getDatabaseUser(self):
        return self.settings['database_user']

    def getDatabasePasswd(self):
        return self.settings['database_passwd']
