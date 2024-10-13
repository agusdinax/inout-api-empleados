class Flash:
    def __init__(self):
        self.messages = []

    def set(self, message: str):
        self.messages.append(message)

    def get(self):
        messages = self.messages.copy()  
        self.clear() 
        return messages

    def clear(self):
        self.messages = []
