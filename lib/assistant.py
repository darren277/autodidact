""""""
import json
import time

import openai
from openai import OpenAI

from flask_sse import sse

from lib.tool_funcs import tool_funcs_dict, process_tool_func
from logger import Logger
from settings import SYSTEM_PROMPT, GPT_ASSISTANT_NAME, GPT_MODEL_ID, LOG_LEVEL

print(SYSTEM_PROMPT)

# tools = [
#     content_rerieval_tool,
#     assessment_generation_tool,
#     progress_tracking_tool
# ]

tools = [
    {
"type": "function",
    "function": {
        "name": "addition",
        "description": "Add two numbers together",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {
                    "type": "number",
                    "description": "The X value to be added.",
                },
                "y": {
                    "type": "number",
                    "description": "The Y value to be added",
                },
            },
            "required": ["x", "y"]
        }
    }
    }
]

client = OpenAI()


my_assistant = client.beta.assistants.create(
    instructions=SYSTEM_PROMPT,
    name=GPT_ASSISTANT_NAME,
    tools=tools,
    model=GPT_MODEL_ID
)


def serialize(event):
    return dict(
        event=event.event,
        data=dict(
            delta=dict(
                content=[
                    dict(
                        text=dict(
                            value=event.data.delta.content[i].text.value
                        )
                    ) for i in range(len(event.data.delta.content))
                ]
            )
        )
    )


def handle_assistant_response(app, question: str, py_thread_id):
    with app.app_context():
        #asm = AssistantStateMachine(py_thread_id, question, tools)
        #asm.start()
        ...

