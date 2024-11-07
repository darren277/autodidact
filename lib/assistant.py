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
            return (False, True)#run_active = False# and loop break...
        self.logger.debug(f"Event state changed to: {event.event}, Data: {event.data}")
        if event.event == 'thread.message.delta':
            # Stream the assistant's response token by token
            sse.publish({"message": serialize(event), "type": "message_delta"}, type='assistant_response', channel=self.py_thread_id)
        elif event.event == 'thread.run.step.delta':
            # Stream the assistant's response token by token
            tool_call = event.data.delta.step_details.tool_calls[0]
            print('tool_call', tool_call)
            tool_call_output = tool_call.function.arguments
            ###if content: sse.publish({"message": content, "type": "step_delta"}, type='assistant_response', channel=py_thread_id)
        elif event.event == 'thread.run.requires_action':
            return self.process_tool_calls(event.data.required_action.submit_tool_outputs.tool_calls, event.data.id)
        elif event.event in ['thread.run.step.completed']:
            self.logger.debug("Step completed successfully.")# The assistant might continue to produce messages; continue processing.
            return self.run_active, False, None
        elif event.event == 'thread.run.completed':
            self.logger.debug("Run completed successfully.")
            return (False, True, None)#run_active = False; break
        else:
            self.logger.warn(f"Unhandled event type: {event.event}")
            #continue
        return (self.run_active, False, None)

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

    def process_tool_calls(self, tool_calls, event_data_id) -> (bool, bool, bool):
        # Handle tool calls and submit outputs
        self.tool_outputs = []
        # is event_data_id == self.run_id?
        """ NEW RUN IS STARTED HERE (?) """

        for tool_call in tool_calls:
            self.process_tool_call(tool_call)

        self.run_id = event_data_id
        try:
            print("DEBUG TOOL OUPUTS", self.tool_outputs)
            response = client.beta.threads.runs.submit_tool_outputs(thread_id=self.llm_thread.id, run_id=self.run_id, tool_outputs=self.tool_outputs)
            print(f"-------------------RESPONSE: {response}")
            self.logger.debug(f"Submitted tool outputs for action: {self.tool_outputs}")
            return (False, False, None)
        except openai.BadRequestError as e:
            self.logger.error(f"Error submitting tool outputs: {e}")
            return (False, True, None)
        except Exception as e:
            self.logger.error(f"Unexpected error submitting tool outputs: {e}")
            return (False, True, None)

    def process_run_stream(self):
        for event in self.run:
            self.logger.debug(f"Received event: {event.event}, Data: {event.data}")
            result = self.check_event(event)
            if result[0]: self.run_active = False
            if result[1]: break
            if result[2]: self.publish(**result[2])
            # Update last event time to prevent timeout
            self.last_event_time = time.time()
        self.poll()
        # I'd like to know what 4052 and 3559 total to.
        for event in self.run:
            self.logger.debug(f"Received event: {event.event}, Data: {event.data}")
            result = self.check_event(event)
            if result[0]: self.run_active = False
            if result[1]: break
            if result[2]: self.publish(**result[2])
            # Update last event time to prevent timeout
            self.last_event_time = time.time()

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

