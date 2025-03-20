""""""
from openai import OpenAI

from settings import *

client = OpenAI()


class Completions:
    def __init__(self, model: str, system_prompt: str):
        self.model = model
        self.system_prompt = system_prompt

    def complete(self, msg: str):
        all_messages = [{"role": 'system', "content": self.system_prompt}]
        all_messages.append({"role": 'user', "content": msg})
        result = client.chat.completions.create(model=self.model, messages=all_messages)
        content = result.choices[0].message.content
        return content
