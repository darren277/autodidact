""""""
from typing import List, Optional, Dict, Any
import json


class Text:
    def __init__(self, annotations: List[Any], value: str):
        self.annotations = annotations
        self.value = value


class TextContentBlock:
    def __init__(self, text: Text, type: str):
        self.text = text
        self.type = type

class Message:
    def __init__(self, id: str, assistant_id: str, attachments: List[Attachment], completed_at: Optional[int], content: List[ContentBlock], created_at: int, incomplete_at: Optional[int], incomplete_details: Optional[IncompleteDetails], metadata: Dict[str, Any], object: str, role: str, run_id: str, status: Optional[str], thread_id: str):
        self.id = id
        self.assistant_id = assistant_id
        self.attachments = attachments
        self.completed_at = completed_at
        self.content = content
        self.created_at = created_at
        self.incomplete_at = incomplete_at
        self.incomplete_details = incomplete_details
        self.metadata = metadata
        self.object = object
        self.role = role
        self.run_id = run_id
        self.status = status
        self.thread_id = thread_id

    def __str__(self):
        return f"Message(id={self.id}, assistant_id={self.assistant_id}, attachments={self.attachments}, completed_at={self.completed_at}, content={self.content}, created_at={self.created_at}, incomplete_at={self.incomplete_at}, incomplete_details={self.incomplete_details}, metadata={self.metadata}, object={self.object}, role={self.role}, run_id={self.run_id}, status={self.status}, thread_id={self.thread_id})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        return Message(**d)

    def to_json(self):
        return json.dumps(self.to_dict())
