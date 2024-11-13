""""""

class TruncationStrategy:
    def __init__(self, type: str, last_messages: int):
        self.type = type
        self.last_messages = last_messages

