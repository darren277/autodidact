""""""
from lib.assistant.initialize import logger
from lib.assistant.process_run_events import process_run_events
from lib.assistant.start_assistant_run import start_assistant_run

DEFAULT_PROMPT = "Add 1234 and 5678 then multiply by 2."
DEFAULT_ASSISTANT_ID = "asst_X0dIT6aOTHFQgJNE923sjv8E"


class AssistantHandler:
    def __init__(self, prompt: str, assistant_id: str, tools: [dict] = None):
        self.prompt = prompt
        self.assistant_id = assistant_id
        self.tools = tools

        self._app = None
        self._logger = logger

        self._full_message = ""

    def initialize_app(self, app):
        self._app = app

    def front_end_callback(self, message):
        # Replace this with your actual front-end streaming implementation
        logger.debug(f"Assistant: {message}")
        self._full_message += message[0].text.value

        #def handle_assistant_response(app, question: str, py_thread_id):
        if self._app:
            with self._app.app_context():
                #asm = AssistantStateMachine(py_thread_id, question, tools)
                #asm.start()
                ...

    def run(self):
        from lib.tools.arithmetic import tools as arithmetic_tools

        tools = self.tools or arithmetic_tools
        event_stream, thread_id = start_assistant_run(self.prompt, self.assistant_id, tools)
        process_run_events(event_stream, thread_id, self.front_end_callback)

        self._logger.debug(f"Full message: {self._full_message}")

