""""""
from lib.assistant.initialize import client


def start_assistant_run(prompt, assistant_id, tools=None):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(thread.id, role="user", content=prompt)
    run_args = {"thread_id": thread.id, "assistant_id": assistant_id, "stream": True}
    if tools: run_args["tools"] = tools
    event_stream = client.beta.threads.runs.create(**run_args)
    return event_stream, thread.id
