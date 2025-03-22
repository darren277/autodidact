""""""
from lib.tts.main import construct_presentation_from_structured_notes
from tests.example_structured_notes import data


if __name__ == '__main__':
    i = input("Note that this will make OpenAI API calls and write files to the filesystem. Continue? (y/n): ")
    if i.lower() == 'y':
        construct_presentation_from_structured_notes(data)
