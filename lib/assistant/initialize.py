""""""
import time
import json

from openai import OpenAI

from settings import *

client = OpenAI()

client = OpenAI()

from settings import SYSTEM_PROMPT

print(SYSTEM_PROMPT)

# tools = [
#     content_rerieval_tool,
#     assessment_generation_tool,
#     progress_tracking_tool
# ]



#my_assistant = client.beta.assistants.create(instructions=SYSTEM_PROMPT, name=GPT_ASSISTANT_NAME, tools=tools, model=GPT_MODEL_ID)

from logger import Logger

logger = Logger(level=logging.DEBUG)

def get_run_status(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    return run.status
