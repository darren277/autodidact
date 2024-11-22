""""""
from typing import List, Any


class TextDelta:
    def __init__(self, annotations: List[Any] or None, value: str):
        self.annotations = annotations
        self.value = value


class TextDeltaBlock:
    def __init__(self, index: int, type: str, text: TextDelta):
        self.index = index
        self.type = type
        self.text = text


class MessageDelta:
    def __init__(self, content: List[TextDeltaBlock], role: str or None):
        self.content = content
        self.role = role


class MessageDeltaEvent:
    def __init__(self, id: str, delta: MessageDelta, object: str):
        self.id = id
        self.delta = delta
        self.object = object
