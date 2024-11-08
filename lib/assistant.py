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

class AssistantStateMachine:
    def __init__(self, py_thread_id, prompt: str, tools: [dict] = None):
        self.py_thread_id = py_thread_id
        self.prompt = prompt
        #self.run_active = False
        self.run_active = True
        self.last_event_time = time.time()
        self.MAX_EVENT_WAIT_TIME = 60

        self.llm_thread = client.beta.threads.create()
        self.llm_thread_message = client.beta.threads.messages.create(self.llm_thread.id, role="user", content=prompt)
        run_kwargs = dict(thread_id=self.llm_thread.id, assistant_id=my_assistant.id, stream=True)
        if tools: run_kwargs['tools'] = tools
        self.run = client.beta.threads.runs.create(**run_kwargs)

        self.logger = Logger(level=LOG_LEVEL)

        self._event_state = 'starting'

    def start(self):
        try:
            self.process_run_stream()
        except Exception as e:
            self.logger.error(f"Exception occurred during event processing: {e}")
            self.run_active = False

    def check_event(self, event):
        if event.event in ['thread.run.failed', 'thread.run.step.failed']:
            self.logger.error(f"{event.event.split('.')[-2].capitalize()} failed with error: {event.data.last_error}")
            return False, True, None  # Stop processing
        elif event.event == 'thread.message.delta':
            # Stream the assistant's response
            self.publish(
                data={"message": serialize(event), "type": "message_delta"},
                type='assistant_response',
                channel=self.py_thread_id
            )
        elif event.event == 'thread.run.requires_action':
            return self.process_tool_calls(event.data.required_action.submit_tool_outputs.tool_calls, event.data.id)
        elif event.event == 'thread.run.completed':
            self.logger.info("Run completed successfully.")
            return False, True, None  # Stop processing
        else:
            self.logger.warning(f"Unhandled event type: {event.event}")

        return True, False, None  # Continue processing

    def process_tool_call(self, tool_call):
        tool_call_id, function_name, arguments = tool_call.id, tool_call.function.name, tool_call.function.arguments
        self.logger.debug(f"Tool call ID: {tool_call_id}, Function name: {function_name}, Arguments: {arguments}")
        try:
            tool_call_result = process_tool_func(function_name, **json.loads(arguments))
            self.tool_outputs.append({"tool_call_id": tool_call_id, "output": tool_call_result})
            self.logger.debug(f"Prepared output for tool call {tool_call_id}: {tool_call_result}")
        except Exception as e:
            result = f"Error processing tool call {tool_call_id}: {e}"
            self.logger.error(result)
            self.tool_outputs.append({"tool_call_id": tool_call_id, "output": result})

    def process_tool_calls(self, tool_calls, event_data_id):
        # Handle tool calls and submit outputs
        self.tool_outputs = []

        for tool_call in tool_calls:
            self.process_tool_call(tool_call)

        self.run_id = event_data_id
        try:
            self.logger.debug(f"Submitting tool outputs: {self.tool_outputs}")
            response = client.beta.threads.runs.submit_tool_outputs(
                thread_id=self.llm_thread.id, run_id=self.run_id, tool_outputs=self.tool_outputs
            )
            self.logger.debug(f"Submitted tool outputs: {response}")

            # Re-initialize the event stream
            #self.run = client.beta.threads.runs.continue_events(thread_id=self.llm_thread.id, run_id=self.run_id)
            #self.run = client.beta.threads.runs.retrieve(thread_id=self.llm_thread.id, run_id=self.run_id)

            return True, False, None  # Continue processing
        except Exception as e:
            self.logger.error(f"Error submitting tool outputs: {e}")
            return False, True, None  # Stop processing due to error

    def process_run_stream(self):
        while self.run_active:
            try:
                #self.run = client.beta.threads.runs.retrieve(thread_id=self.llm_thread.id, run_id=self.run_id, stream=True)
                # event, yo! ('id', 'run_ozIC5w9fU7k0o3njLfH67bMw')

                for event in self.run:
                    print('event, yo!', event)
                    self.logger.debug(f"Received event: {event.event}, Data: {event.data}")
                    result = self.check_event(event)
                    if not result[0]:  # run_active
                        self.run_active = False
                        break
                    if result[1]:  # should_break
                        break
                    if result[2]:
                        self.publish(**result[2])
                    self.last_event_time = time.time()
                else:
                    # If the for loop completes naturally, re-enter the loop
                    continue
                break  # Break the while loop if inner loop is broken
            except Exception as e:
                self.logger.error(f"Exception in process_run_stream: {e}")
                self.run_active = False
                break

        if self.run_active:
            self.poll()

    def publish(self, **kwargs): sse.publish(**kwargs)

    def process_completed_run(self):
        self.logger.info("Run completed successfully after polling.")
        self.run_active = False
        messages = client.beta.threads.messages.list(thread_id=self.llm_thread.id)# Fetch the final messages and stream them
        for message in messages:
            print("MESSAGE:", message)
            if message.role == 'assistant':
                self.publish(data={"message": message.content[0].text.value, "type": "completed_message"}, type='assistant_response', channel=self.py_thread_id)

    def poll(self, poll_interval: int = 2):
        # If the run is still active after the stream ends, optionally poll the run status
        if self.run_active:
            self.logger.warn("Run did not complete before the stream ended.")
            # Optionally, you can implement polling here if necessary.
            self.polling_start_time = time.time()
            self.MAX_POLLING_TIME = 300  # Poll for up to 300 seconds

            while self.run_active and (time.time() - self.polling_start_time) < self.MAX_POLLING_TIME:
                try:
                    run = client.beta.threads.runs.retrieve(thread_id=self.llm_thread.id, run_id=self.run_id)
                    self.logger.debug(f"Polled run status: {run.status}")
                    if run.status == 'completed':
                        self.process_completed_run()
                    elif run.status == 'failed':
                        self.run_active = False
                        self.logger.error(f"Run failed with error: {run.last_error}")
                    else:
                        print(5*"!!!!!!!!!!!!!!!!!!!!!!!!Run status:\n", run.status)
                        # Run is still in progress, wait before polling again
                        time.sleep(poll_interval)
                except Exception as e:
                    self.logger.error(f"Error polling run status: {e}")
                    self.run_active = False
                    break
            if self.run_active:
                self.logger.error("Run did not complete within the maximum polling time.")
        else:
            print("GUH!?")


def handle_assistant_response(app, question: str, py_thread_id):
    with app.app_context():
        asm = AssistantStateMachine(py_thread_id, question, tools)
        asm.start()

