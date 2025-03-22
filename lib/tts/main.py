""""""
import asyncio
from typing import Tuple

from openai import AsyncOpenAI

from lib.completions.main import Completions
from lib.tts.personalities import voices, assign_voice

# Needed to set the OpenAI API key
from settings import *
from utils.typedefs import StructuredNotes

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

    def __str__(self):
        return "\n".join([f"{name}: {text}" for name, text in self.lines])


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


from lib.tts.personalities import CHARACTERS_ARRAY
from lib.tts.prompts import construct_dramatized_narrative_prompt, construct_structured_notes_presentation_prompt
import random


def split_lines(text):
    dialogue = []
    current_name = None
    for line in text.split('\n'):
        line = line.strip()
        if line:
            name = line.split(':')[0]
            if '*' in name: name = name.replace('*', '').lstrip().rstrip()
            try:
                text = line.split(':')[1].rstrip()
                current_name = name
                dialogue.append((name, text))
            except IndexError:
                # Assume that the line is a continuation of the previous line
                text = line
                dialogue.append((current_name, text))
    return dialogue


TEST_INPUT_TEXT = "The lorems discovered the ipsum in 1967. They began cultivating ipsum in large quantities, which led to it becoming their primary source of sustenance, and a major export leveraged in trade with surrounding societies."

def construct_conversation(input_text: str = TEST_INPUT_TEXT) -> None:
    '''
    Construct a dramatic narrative conversation based on the input text.
    Writes the prompt, dialogue, and audio to files.
    :param input_text:
    :return:
    '''
    char1 = random.choice(CHARACTERS_ARRAY)
    char2 = random.choice(CHARACTERS_ARRAY)

    prompt = construct_dramatized_narrative_prompt(char1["name"], char1["description"], char2["name"], char2["description"], input_text)

    SYSTEM_PROMPT = """
    You are an expert writer with a passion for education. You take in a description of some characters and an associated piece of text and turn it into a dialogue between two characters.
    """

    completions = Completions('gpt-4o', SYSTEM_PROMPT)
    result = completions.complete(prompt)
    with open("prompt.txt", "w") as f: f.write(result)

    dialogue_input = split_lines(result)
    dialogue = Dialogue(*dialogue_input)

    with open("dialogue.txt", "w") as f: f.write(str(dialogue))

    persona1 = TTS("gpt-4o-mini-tts", assign_voice(char1), char1['descriptors'])
    persona2 = TTS("gpt-4o-mini-tts", assign_voice(char2), char2['descriptors'])

    dramatic_narrative = Conversation(
        dialogue,
        **{char1["name"].lower(): persona1, char2["name"].lower(): persona2}
    )

    audio = asyncio.run(dramatic_narrative.construct_audio())
    with open("dramatic_narrative.wav", "wb") as f: f.write(audio)


def construct_presentation_from_structured_notes(structured_notes: StructuredNotes or dict):
    from lib.tts.personalities import MAIN_NARRATOR, MAIN_NARRATOR_VOICE, INNOVATOR, INNOVATOR_VOICE, HISTORIAN, HISTORIAN_VOICE

    main_narrator_persona = TTS("gpt-4o-mini-tts", MAIN_NARRATOR_VOICE, MAIN_NARRATOR["descriptors"])
    innovator_persona = TTS("gpt-4o-mini-tts", INNOVATOR_VOICE, INNOVATOR["descriptors"])
    historian_persona = TTS("gpt-4o-mini-tts", HISTORIAN_VOICE, HISTORIAN["descriptors"])

    SYSTEM_PROMPT = """
    You are an expert writer with a passion for education. You take in a structured set of notes and turn it into a compelling presentation.
    """

    prompt = construct_structured_notes_presentation_prompt(structured_notes)
    completions = Completions('gpt-4o', SYSTEM_PROMPT)
    result = completions.complete(prompt)

    with open("presentation_prompt.txt", "w") as f: f.write(result)

    dialogue_input = split_lines(result)
    dialogue = Dialogue(*dialogue_input)

    with open("presentation_dialogue.txt", "w") as f: f.write(str(dialogue))

    presentation = Conversation(
        dialogue,
        **{MAIN_NARRATOR["name"].lower(): main_narrator_persona, INNOVATOR["name"].lower(): innovator_persona, HISTORIAN["name"].lower(): historian_persona}
    )

    audio = asyncio.run(presentation.construct_audio())
    with open("presentation.wav", "wb") as f: f.write(audio)

