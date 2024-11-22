""""""
from flask_sse import sse

from lib.assistant.initialize import logger
from lib.assistant.process_run_events import process_run_events
from lib.assistant.start_assistant_run import start_assistant_run

DEFAULT_PROMPT = "Add 1234 and 5678 then multiply by 2."
DEFAULT_ASSISTANT_ID = "asst_X0dIT6aOTHFQgJNE923sjv8E"


class AssistantHandler:
    def __init__(self, prompt: str, assistant_id: str or None, tools: [dict] = None):
        self.prompt = prompt
        # TODO: This should not default to a constant in production.
        self.assistant_id = assistant_id or DEFAULT_ASSISTANT_ID
        self.tools = tools

        self._app = None
        self._logger = logger
        self._py_thread_id = None

        self._full_message = ""

        self._r = None
        self._FLASK_SSE = False

    def initialize_app(self, app):
        self._app = app

    def front_end_callback(self, message):
        logger.debug(f"Assistant: {message}")
        self._full_message += message[0].text.value

        #def handle_assistant_response(app, question: str, py_thread_id):
        if self._app:
            with self._app.app_context():
                #asm = AssistantStateMachine(py_thread_id, question, tools)
                #asm.start()
                # serialize(event), "type": "message_delta"
                sse = self._r
                #sse.publish({"message": message[0].text.value, "type": "message_delta"}, type='assistant_response')#, channel=self._py_thread_id)
                self.publish(self._py_thread_id, message[0].text.value)
                ...

    def publish(self, message):
        if self._FLASK_SSE:
            sse.publish({"message": message[0].text.value, "type": "message_delta"}, type='assistant_response')  # , channel=self._py_thread_id)
        else:
            self._r.publish(self._py_thread_id, message[0].text.value)


    def run(self, py_thread_id):
        from lib.tools.arithmetic import tools as arithmetic_tools

        self._py_thread_id = py_thread_id

        tools = self.tools or arithmetic_tools
        event_stream, thread_id = start_assistant_run(self.prompt, self.assistant_id, tools)
        process_run_events(event_stream, thread_id, self.front_end_callback)

        self._logger.debug(f"Full message: {self._full_message}")

