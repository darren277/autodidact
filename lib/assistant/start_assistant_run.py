""""""
from openai import OpenAI


def start_assistant_run(prompt, assistant_id, tools=None, api_key=None):
    # Create client with user's API key if provided, otherwise use default
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        from lib.assistant.initialize import client
    
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(thread.id, role="user", content=prompt)
    run_args = {"thread_id": thread.id, "assistant_id": assistant_id, "stream": True}
    if tools: run_args["tools"] = tools
    event_stream = client.beta.threads.runs.create(**run_args)
    return event_stream, thread.id
