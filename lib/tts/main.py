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


