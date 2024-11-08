import os

import openai
import time
import json

from openai import OpenAI

from settings import *

client = OpenAI()


def start_assistant_run(prompt, assistant_id, tools=None):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(thread.id, role="user", content=prompt)
    run_args = {'thread_id': thread.id, 'assistant_id': assistant_id, 'stream': True}
    if tools: run_args['tools'] = tools
    event_stream = client.beta.threads.runs.create(**run_args)
    return event_stream, thread.id


def process_run_events(initial_event_stream, thread_id, front_end_callback, tool_outputs=None):
    run_active = True
    run_id = None
    event_stream = initial_event_stream
    while run_active:
        try:
            print("================> EVENT STREAM", type(event_stream), event_stream)
            print(openai.lib.streaming._assistants.AssistantStreamManager)
            if 'AssistantStreamManager' in str(type(event_stream)): print(event_stream.__dir__())

            with event_stream as es:
                for event in es:
                    event_type = event.event
                    print(f"Received event: {event_type}")

                    # Extract run_id from the 'thread.run.started' event
                    if event_type == 'thread.run.created' and run_id is None:
                        run_id = event.data.id
                        print(f"Extracted run_id: {run_id}")
                    else:
                        print("EVENT TYPE:", event_type)
                        if run_id is None:
                            print("-----> Run ID not obtained; cannot proceed.")
                            run_active = False
                            break

                    # Handle the event
                    result, new_event_stream = handle_event(event, run_id, thread_id, front_end_callback)
                    if result == 'switch_stream':
                        # Switch to the new event stream returned from submit_tool_outputs
                        event_stream = new_event_stream
                        break  # Break the for loop to start with the new event stream
                    elif result == 'stop':
                        run_active = False
                        break
                    # Continue processing if result is 'continue'

                else:
                    # If the event stream ends naturally, check if the run is completed
                    if run_id:
                        run_status = get_run_status(thread_id, run_id)
                        if run_status in ['completed', 'failed', 'cancelled']:
                            run_active = False
                        else:
                            # Wait briefly and re-initialize the event stream
                            time.sleep(1)
                            #event_stream = openai.ThreadRun.events(thread_id=thread_id, run_id=run_id, stream=True)
                            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                            #stream = openai.beta.threads.runs.submitToolOutputsStream(thread, run_id, tool_outputs)
                            stream = client.beta.threads.runs.submit_tool_outputs_stream(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)
                            try:
                                event_stream = run.events(stream=True)
                            except Exception as e:
                                print(f"------> Error re-initializing event stream: {e}")
                                run_active = False
                    else:
                        print("Run ID not obtained; cannot proceed.")
                        run_active = False
        except Exception as e:
            print(f"Error processing events: {e}")
            run_active = False
            break


def handle_event(event, run_id, thread_id, front_end_callback):
    event_type = event.event
    if event_type == 'thread.run.started':
        # run_id has been extracted; no further action needed here
        return 'continue', None
    elif event_type == 'thread.message.delta':
        # Stream message content to the front end
        content = event.data.delta.content
        if content:
            front_end_callback(content)
        return 'continue', None
    elif event_type == 'thread.run.requires_action':
        # Handle tool calls
        tool_calls = event.data.required_action.submit_tool_outputs.tool_calls
        new_event_stream = submit_tool_outputs(tool_calls, run_id, thread_id)
        ####return 'restart_stream', None
        return 'switch_stream', new_event_stream
    elif event_type == 'thread.run.completed':
        print("Run completed successfully.")
        return 'stop', None
    elif event_type == 'thread.run.failed':
        print(f"Run failed with error: {event.data.last_error}")
        return 'stop', None
    else:
        print(f"Unhandled event type: {event_type}")
        return 'continue', None


def submit_tool_outputs(tool_calls, run_id, thread_id):
    tool_outputs = []
    for tool_call in tool_calls:
        tool_call_id = tool_call.id
        function_name = tool_call.function.name
        arguments = tool_call.function.arguments
        # Process the tool call
        output = process_tool_function(function_name, arguments)
        tool_outputs.append({'tool_call_id': tool_call_id, 'output': output})

    # Submit tool outputs with stream=True to get the new event stream
    new_event_stream = client.beta.threads.runs.submit_tool_outputs_stream(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)
    print("Submitted tool outputs:", tool_outputs)
    return new_event_stream  # Return the new event stream


def get_run_status(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    return run.status


def process_tool_function(function_name, arguments):
    args = json.loads(arguments)
    if function_name == 'add_numbers':
        a = args.get('a', 0)
        b = args.get('b', 0)
        result = a + b
        return json.dumps({'result': result})
    else:
        return json.dumps({'error': f"Function '{function_name}' not implemented."})

full_message = ""

def front_end_callback(message):
    # Replace this with your actual front-end streaming implementation
    print(f"Assistant: {message}")
    global full_message

    # [TextDeltaBlock(index=0, type='text', text=TextDelta(annotations=None, value=' is'))]
    full_message += message[0].text.value


def main():
    prompt = "What is the sum of 1234 and 5678?"
    assistant_id = 'asst_X0dIT6aOTHFQgJNE923sjv8E'
    tools = [
        {
            "type": "function",
            "function":
            {
                "name": "add_numbers",
                "description": "Adds two numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "The first number"},
                        "b": {"type": "number", "description": "The second number"},
                    },
                    "required": ["a", "b"],
                },
            }
        }
    ]
    event_stream, thread_id = start_assistant_run(prompt, assistant_id, tools)
    process_run_events(event_stream, thread_id, front_end_callback)

    print("Full message:", full_message)

if __name__ == "__main__":
    main()
