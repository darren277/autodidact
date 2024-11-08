""""""
from lib.assistant.initialize import logger
from lib.assistant.process_run_events import process_run_events
from lib.assistant.start_assistant_run import start_assistant_run

full_message = ""

DEFAULT_PROMPT = "Add 1234 and 5678 then multiply by 2."
DEFAULT_ASSISTANT_ID = "asst_X0dIT6aOTHFQgJNE923sjv8E"


def front_end_callback(message):
    # Replace this with your actual front-end streaming implementation
    logger.debug(f"Assistant: {message}")
    global full_message

    full_message += message[0].text.value

def handle_assistant_response(app, question: str, py_thread_id):
    with app.app_context():
        #asm = AssistantStateMachine(py_thread_id, question, tools)
        #asm.start()
        ...

def main(prompt: str, assistant_id: str, tools: [dict] = None):
    from lib.tools.arithmetic import tools as arithmetic_tools

    tools = tools or arithmetic_tools
    event_stream, thread_id = start_assistant_run(prompt, assistant_id, tools)
    process_run_events(event_stream, thread_id, front_end_callback)

    logger.debug(f"Full message: {full_message}")


if __name__ == "__main__":
    main(prompt=DEFAULT_PROMPT, assistant_id=DEFAULT_ASSISTANT_ID)
