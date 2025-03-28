""""""
import json
from typing import Optional, List, Dict

from lib.assistant.initialize import logger
from lib.assistant.process_run_events import process_run_events
from lib.assistant.start_assistant_run import start_assistant_run

DEFAULT_PROMPT = "Add 1234 and 5678 then multiply by 2."
DEFAULT_ASSISTANT_ID = "asst_X0dIT6aOTHFQgJNE923sjv8E"


class AssistantHandler:
    def __init__(self, prompt: str, assistant_id: Optional[str] = None, tools: Optional[List[Dict]] = None):
        """
        Initialize the AssistantHandler with a prompt and optional assistant ID and tools.

        Args:
            prompt: The user's question or prompt
            assistant_id: The OpenAI Assistant ID to use (optional)
            tools: List of tools to make available to the assistant (optional)
        """
        self.prompt = prompt
        self.assistant_id = assistant_id
        self.tools = tools or []

        # Internal state
        self._full_message = ""
        self._py_thread_id = None
        self._r = None  # Redis client
        self._FLASK_SSE = False  # Flag to determine which streaming method to use

    def front_end_callback(self, message):
        """
        Callback function that processes each message chunk from the OpenAI API.

        This method publishes the message chunk to the appropriate channel
        for streaming to the frontend.

        Args:
            message: Message chunk from the OpenAI API
        """
        if not message or not hasattr(message[0], 'text') or not hasattr(message[0].text, 'value'):
            logger.warning("Received invalid message format")
            return

        # Extract the text from the message
        text_value = message[0].text.value
        logger.debug(f"Assistant: {text_value}")

        # Append to the full message
        self._full_message += text_value

        # Publish the message chunk for streaming
        self.publish(text_value)

    def publish(self, message_text):
        """
        Publish a message to the appropriate streaming channel.

        Args:
            message_text: Text content to publish
        """
        if self._FLASK_SSE:
            # When using Flask-SSE (not recommended based on your experience)
            from flask_sse import sse
            sse.publish(
                {"message": message_text, "type": "message_delta"},
                type='assistant_response'
            )
        else:
            # When using Redis directly (recommended)
            if self._r and self._py_thread_id:
                self._r.publish(self._py_thread_id, message_text)
            else:
                logger.error("Cannot publish: Redis or thread_id not set")

    def run(self, thread_id: str):
        """
        Run the assistant with the provided prompt and stream the response.

        Args:
            thread_id: Unique identifier for this conversation
        """
        # Store the thread ID for publishing
        self._py_thread_id = thread_id

        try:
            # Start the assistant run - replace with your actual implementation
            event_stream, openai_thread_id = start_assistant_run(
                self.prompt,
                self.assistant_id,
                self.tools
            )

            # Process events and call the callback for each message chunk
            process_run_events(
                event_stream,
                openai_thread_id,
                self.front_end_callback
            )

            # Log the complete message when done
            logger.debug(f"Full message: {self._full_message}")

            # Optionally send a completion signal
            if self._r and self._py_thread_id:
                self._r.publish(f"{self._py_thread_id}_complete", json.dumps({"complete": True, "full_message": self._full_message}))

        except Exception as e:
            logger.error(f"Error running assistant: {str(e)}")
            # Try to notify the client about the error
            if self._r and self._py_thread_id:
                self._r.publish(
                    self._py_thread_id,
                    f"An error occurred while processing your request: {str(e)}"
                )

