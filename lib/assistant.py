""""""
import json
import time

import openai
from openai import OpenAI

from flask_sse import sse

#from lib.funcs.main import fetch_learning_material, generate_practice_problem, record_student_progress

#from lib.tools.assessment_generation import assessment_generation_tool
#from lib.tools.content_retrieval import content_rerieval_tool
#from lib.tools.progress_tracking import progress_tracking_tool
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
    logger = Logger(level=LOG_LEVEL)

    with app.app_context():
        thread = client.beta.threads.create()

        thread_message = client.beta.threads.messages.create(
            thread.id,
            role="user",
            content=question
        )

        run_stream = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=my_assistant.id,
            tools=tools,
            stream=True
        )

        run_active = True
        last_event_time = time.time()
        MAX_EVENT_WAIT_TIME = 60  # Maximum time to wait between events

        try:
            for event in run_stream:
                logger.debug(f"Received event: {event.event}, Data: {event.data}")

                # Update last event time to prevent timeout
                last_event_time = time.time()

                if event.event == 'thread.message.delta':
                    # Stream the assistant's response token by token
                    #content = event.data.get('content', '')
                    # delta.step_details.tool_calls
                    sse.publish({"message": serialize(event), "type": "message_delta"}, type='assistant_response', channel=py_thread_id)
                elif event.event == 'thread.run.step.delta':
                    # Stream the assistant's response token by token
                    tool_call = event.data.delta.step_details.tool_calls[0]
                    print('tool_call', tool_call)
                    tool_call_output = tool_call.function.arguments
                    ###if content: sse.publish({"message": content, "type": "step_delta"}, type='assistant_response', channel=py_thread_id)
                elif event.event == 'thread.run.requires_action':
                    # Handle tool calls and submit outputs
                    tool_outputs = []

                    """ NEW RUN IS STARTED HERE """

                    for tool_call in event.data.required_action.submit_tool_outputs.tool_calls:
                        tool_call_id = tool_call.id
                        function_name = tool_call.function.name
                        arguments = tool_call.function.arguments
                        logger.debug(f"Tool call ID: {tool_call_id}, Function name: {function_name}, Arguments: {arguments}")

                        try:
                            # if function_name == 'fetch_learning_material':
                            #     result = fetch_learning_material(**json.loads(arguments))
                            # elif function_name == 'generate_practice_problem':
                            #     result = generate_practice_problem(**json.loads(arguments))
                            # elif function_name == 'record_student_progress':
                            #     result = record_student_progress(**json.loads(arguments))
                            if function_name == 'addition':
                                # Tool call ID: call_zMJcq1Wcl0UZ78lRozw5Qvwg, Function name: addition, Arguments: {"x":4052,"y":3559}
                                args = json.loads(arguments)
                                logger.debug(f"ADDITION ARGS: {args}")
                                add_func = lambda x, y: x + y
                                # Error submitting tool outputs: Error code: 400 - {'error': {'message':
                                # -- "Invalid type for 'tool_outputs[0].output': expected a string, but got an integer instead.",
                                # -- 'type': 'invalid_request_error', 'param': 'tool_outputs[0].output', 'code': 'invalid_type'}}
                                result = str(add_func(args['x'], args['y']))
                            else:
                                result = "Function not recognized."

                            if not result:
                                result = "No output generated for this tool call."

                            tool_outputs.append({"tool_call_id": tool_call_id, "output": result})
                            logger.debug(f"Prepared output for tool call {tool_call_id}: {result}")
                        except Exception as e:
                            result = f"Error processing tool call {tool_call_id}: {e}"
                            logger.error(result)
                            tool_outputs.append({"tool_call_id": tool_call_id, "output": result})

                    # Submit tool outputs
                    ####run_id = event.data.run_id  # Ensure run_id is correctly retrieved
                    run_id = event.data.id
                    try:
                        response = client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread.id,
                            run_id=run_id,
                            tool_outputs=tool_outputs
                        )
                        print(f"-------------------RESPONSE: {response}")
                        logger.debug(f"Submitted tool outputs for action: {tool_outputs}")
                    except openai.BadRequestError as e:
                        logger.error(f"Error submitting tool outputs: {e}")
                        break
                    except Exception as e:
                        logger.error(f"Unexpected error submitting tool outputs: {e}")
                        break

                elif event.event == 'thread.run.step.completed':
                    logger.debug("Step completed successfully.")
                    # The assistant might continue to produce messages; continue processing.

                elif event.event == 'thread.run.completed':
                    logger.debug("Run completed successfully.")
                    run_active = False
                    break

                elif event.event == 'thread.run.failed':
                    logger.error(f"Run failed with error: {event.data.last_error}")
                    run_active = False
                    break

                elif event.event == 'thread.run.step.failed':
                    logger.error(f"Step failed with error: {event.data.last_error}")
                    run_active = False
                    break

                else:
                    logger.warn(f"Unhandled event type: {event.event}")
                    continue

            # If the run is still active after the stream ends, optionally poll the run status
            if run_active:
                logger.warn("Run did not complete before the stream ended.")
                # Optionally, you can implement polling here if necessary.
                polling_start_time = time.time()
                MAX_POLLING_TIME = 300  # Poll for up to 300 seconds

                while run_active and (time.time() - polling_start_time) < MAX_POLLING_TIME:
                    try:
                        # Fetch the current run status
                        #run = client.beta.threads.runs.get(thread_id=thread.id, run_id=stream.run_id)
                        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run_id)
                        logger.debug(f"Polled run status: {run.status}")

                        if run.status == 'completed':
                            logger.info("Run completed successfully after polling.")
                            run_active = False

                            # Fetch the final messages and stream them
                            messages = client.beta.threads.messages.list(thread_id=thread.id)
                            for message in messages:
                                print("MESSAGE:", message)
                                if message.role == 'assistant':
                                    sse.publish({"message": message.content[0].text.value, "type": "completed_message"}, type='assistant_response', channel=py_thread_id)
                                    ...

                        elif run.status == 'failed':
                            run_active = False
                            logger.error(f"Run failed with error: {run.last_error}")

                        else:
                            print("!!!!!!!!!!!!!!!!!!!!!!!!Run status:", run.status)
                            print("!!!!!!!!!!!!!!!!!!!!!!!!Run status:", run.status)
                            print("!!!!!!!!!!!!!!!!!!!!!!!!Run status:", run.status)
                            print("!!!!!!!!!!!!!!!!!!!!!!!!Run status:", run.status)
                            print("!!!!!!!!!!!!!!!!!!!!!!!!Run status:", run.status)
                            # Run is still in progress, wait before polling again
                            time.sleep(2)

                    except Exception as e:
                        logger.error(f"Error polling run status: {e}")
                        run_active = False
                        break

                if run_active:
                    logger.error("Run did not complete within the maximum polling time.")

        except Exception as e:
            logger.error(f"Exception occurred during event processing: {e}")
            run_active = False

