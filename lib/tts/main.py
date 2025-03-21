""""""
from openai import AsyncOpenAI

from lib.tts.personalities import voices

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

