class Room():
    def __init__(self, name, items):
        self.name=name
        self.items=items

    def pick(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        else:
            return False

    def place(self, item):
        self.items.append(item)

class House():
    def __init__(self, rooms):
        self.rooms=rooms
