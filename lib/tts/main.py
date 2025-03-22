""""""
import asyncio
from typing import Tuple

from openai import AsyncOpenAI

from lib.completions.main import Completions
from lib.tts.personalities import voices, assign_voice

# Needed to set the OpenAI API key
from settings import *

openai = AsyncOpenAI()


class TTS:
    def __init__(self, model: str, voice: str, instructions: str):
        if model not in ["gpt-4o-mini-tts"]:
            raise ValueError(f"Model '{model}' is not available for TTS.")
        self.model = model

        if voice not in voices:
            raise ValueError(f"Voice '{voice}' is not available for model '{model}'.")
        self.voice = voice

        self.instructions = instructions

    async def speak(self, message: str) -> bytes:
        async with openai.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=self.voice,
            input=message,
            instructions=self.instructions,
            response_format="wav"
        ) as response:
            content = await response.read()
        return content


class Dialogue:
    '''
    A dialogue is a collection of lines spoken by different personas.
    The lines are tuples of (persona `name`, text).
    '''
    def __init__(self, *lines: Tuple[str, str]):
        self.lines = lines

class Conversation:
    '''
    Each persona is represented by a TTS object (and a `name` assigned during instantiation).
    '''
    def __init__(self, dialogue: Dialogue, **personas: TTS):
        self.personas = personas
        self.dialogue = dialogue

    async def construct_audio(self) -> bytes:
        audio = b""
        for name, text in self.dialogue.lines:
            persona = self.personas[name.lower()]
            audio += await persona.speak(text)
        return audio


'''
example_conversation = Conversation(
    Dialogue(
        ("Alice", "Hello, how are you today?"),
        ("Bob", "I'm doing well, thank you. How about you?")
    ),
    alice=TTS("gpt-4o-mini-tts", "alloy", "Speak in a friendly tone."),
    bob=TTS("gpt-4o-mini-tts", "ballad", "Speak in a calm tone.")
)

audio = asyncio.run(example_conversation.construct_audio())
with open("conversation.wav", "wb") as f: f.write(audio)
'''


#'''
from lib.tts.personalities import CHARACTERS_ARRAY
from lib.tts.prompts import construct_dramatized_narrative_prompt
import random

char1 = random.choice(CHARACTERS_ARRAY)
char2 = random.choice(CHARACTERS_ARRAY)

prompt = construct_dramatized_narrative_prompt(char1["name"], char1["description"], char2["name"], char2["description"], "The lorems discovered the ipsum in 1967. They began cultivating ipsum in large quantities, which led to it becoming their primary source of sustenance, and a major export leveraged in trade with surrounding societies.")

SYSTEM_PROMPT = """
You are an expert writer with a passion for education. You take in a description of some characters and an associated piece of text and turn it into a dialogue between two characters.
"""

completions = Completions('gpt-4o', SYSTEM_PROMPT)
result = completions.complete(prompt)

def split_lines(text):
    dialogue = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            name = line.split(':')[0]
            text = line.split(':')[1].rstrip()
            dialogue.append((name, text))
    return dialogue

dialogue_input = split_lines(result)
dialogue = Dialogue(*dialogue_input)

persona1 = TTS("gpt-4o-mini-tts", assign_voice(char1), char1['descriptors'])
persona2 = TTS("gpt-4o-mini-tts", assign_voice(char2), char2['descriptors'])

dramatic_narrative = Conversation(
    dialogue,
    **{char1["name"].lower(): persona1, char2["name"].lower(): persona2}
)

audio = asyncio.run(dramatic_narrative.construct_audio())
with open("dramatic_narrative.wav", "wb") as f: f.write(audio)
#'''
