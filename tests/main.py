""""""
from openai import OpenAI

from logger import Logger
from settings import LOG_LEVEL

SIMPLE_PROMPT = "I'm struggling with understanding how to solve quadratic equations. Can you explain it to me?"
PROMPT_TO_ENCOURAGE_DIAGRAM = "I'm struggling with understanding how to solve quadratic equations. Can you explain it to me? I'd appreciate a diagram."
SIMPLE_ADDITION_TOOL_USE = "I'd like to know what 4052 and 3559 total to."
ADD_AND_MULTIPLY_TOOL_COMBO = "Add 1234 and 5678 then multiply by 2."

client = OpenAI()


# TEST: AssistantHandler(prompt=DEFAULT_PROMPT, assistant_id=DEFAULT_ASSISTANT_ID).run()

def list_runs(thread_id: str):
    runs = client.beta.threads.runs.list(thread_id=thread_id)

    for run in runs:
        print(run)


def list_threads(assistant_id: str):
    threads = client.beta.threads.list(assistant_id=assistant_id)

    for thread in threads:
        print(thread)


def list_assistants():
    assistants = client.beta.assistants.list()

    for assistant in assistants:
        print(assistant)

        list_threads(assistant.id)



def test_logger():
    logger = Logger(level=LOG_LEVEL)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")


def test_redis():
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.set('foo', 'bar')
    value = r.get('foo')
    print(value)

    assert value == b'bar'
