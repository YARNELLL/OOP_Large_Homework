import json
import os

USER_DATA_PATH = 'user.txt'

class UserData:
    def __init__(self) -> None:
        print(USER_DATA_PATH, os.path.exists(USER_DATA_PATH))
        if os.path.exists(USER_DATA_PATH):
            with open(USER_DATA_PATH, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}
    
    def save(self):
        with open(USER_DATA_PATH, 'w') as f:
            json.dump(self.data, f)
    
    def get(self, name):
        if self.data.get(name, None) is None:
            self.data[name] = {
                'name': name,
                'win': 0
            }
            self.save()
        print(name, self.data[name])
        return self.data[name]
    
    def win(self, name):
        rec = self.get(name)
        rec['win'] += 1
        self.save()

user_data = UserData()
            