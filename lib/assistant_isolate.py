""""""
import time
import json

from openai import OpenAI

from settings import *

client = OpenAI()

from logger import Logger

logger = Logger(level=logging.DEBUG)

def start_assistant_run(prompt, assistant_id, tools=None):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(thread.id, role="user", content=prompt)
    run_args = {"thread_id": thread.id, "assistant_id": assistant_id, "stream": True}
    if tools: run_args["tools"] = tools
    event_stream = client.beta.threads.runs.create(**run_args)
    return event_stream, thread.id


def process_run_events(initial_event_stream, thread_id, front_end_callback, tool_outputs=None):
    run_active, run_id = True, None
    event_stream = initial_event_stream
    while run_active:
        try:
            with event_stream as es:
                for event in es:
                    event_type = event.event
                    logger.debug(f"Received event: {event_type}")
                    if event_type == "thread.run.created" and run_id is None:
                        run_id = event.data.id
                    else:
                        if run_id is None:
                            logger.debug("-----> Run ID not obtained; cannot proceed.")
                            run_active = False
                            break
                    result, new_event_stream = handle_event(event, run_id, thread_id, front_end_callback)
                    if result == "switch_stream":
                        event_stream = new_event_stream
                        break
                    elif result == "stop":
                        run_active = False
                        break
                else:
                    if run_id:
                        run_status = get_run_status(thread_id, run_id)
                        if run_status in ["completed", "failed", "cancelled"]:
                            run_active = False
                        else:
                            time.sleep(1)
                            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                            stream = (client.beta.threads.runs.submit_tool_outputs_stream(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs))
                            try:
                                event_stream = run.events(stream=True)
                            except Exception as e:
                                logger.debug(f"------> Error re-initializing event stream: {e}")
                                run_active = False
                    else:
                        logger.debug("Run ID not obtained; cannot proceed.")
                        run_active = False
        except Exception as e:
            logger.debug(f"Error processing events: {e}")
            run_active = False
            break


def handle_event(event, run_id, thread_id, front_end_callback):
    event_type = event.event
    if event_type == "thread.run.started":
        return "continue", None
    elif event_type == "thread.message.delta":
        content = event.data.delta.content
        if content: front_end_callback(content)
        return "continue", None
    elif event_type == "thread.run.requires_action":
        tool_calls = event.data.required_action.submit_tool_outputs.tool_calls
        new_event_stream = submit_tool_outputs(tool_calls, run_id, thread_id)
        return "switch_stream", new_event_stream
    elif event_type == "thread.run.completed":
        logger.debug("Run completed successfully.")
        return "stop", None
    elif event_type == "thread.run.failed":
        logger.debug(f"Run failed with error: {event.data.last_error}")
        return "stop", None
    else:
        logger.debug(f"Unhandled event type: {event_type}")
        return "continue", None


def submit_tool_outputs(tool_calls, run_id, thread_id):
    tool_outputs = []
    for tool_call in tool_calls:
        tool_call_id, function_name, arguments = tool_call.id, tool_call.function.name, tool_call.function.arguments
        output = process_tool_function(function_name, arguments)
        tool_outputs.append({"tool_call_id": tool_call_id, "output": output})

    new_event_stream = client.beta.threads.runs.submit_tool_outputs_stream(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)
    logger.debug("Submitted tool outputs:", tool_outputs)
    return new_event_stream


def get_run_status(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    return run.status


def process_tool_function(function_name, arguments):
    args = json.loads(arguments)
    if function_name == "add_numbers":
        logger.debug("________________________________ADD NUMBERS____________________________________")
        a = args.get("a", 0)
        b = args.get("b", 0)
        result = a + b
        return json.dumps({"result": result})
    if function_name == "multiply_numbers":
        logger.debug("________________________________MULTIPLY NUMBERS____________________________________")
        a = args.get("a", 0)
        b = args.get("b", 0)
        result = a * b
        return json.dumps({"result": result})
    else:
        return json.dumps({"error": f"Function '{function_name}' not implemented."})


full_message = ""


def front_end_callback(message):
    # Replace this with your actual front-end streaming implementation
    logger.debug(f"Assistant: {message}")
    global full_message

    full_message += message[0].text.value


def main():
    from lib.tools.arithmetic import tools
    prompt = "Add 1234 and 5678 then multiply by 2."
    assistant_id = "asst_X0dIT6aOTHFQgJNE923sjv8E"
    event_stream, thread_id = start_assistant_run(prompt, assistant_id, tools)
    process_run_events(event_stream, thread_id, front_end_callback)

    logger.debug("Full message:", full_message)


if __name__ == "__main__":
    main()
