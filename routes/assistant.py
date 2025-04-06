""""""
import threading

from flask import request, jsonify, Response

from lib.assistant.main import AssistantHandler
from settings import DEFAULT_ASSISTANT_ID


def ask_route(r):
    # Extract question from form or JSON data
    if request.is_json:
        data = request.get_json()
        question = data.get('question')
    else:
        question = request.form.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    assistant_id = request.form.get('assistant_id', DEFAULT_ASSISTANT_ID)

    # Generate a unique thread ID based on client IP and timestamp
    from datetime import datetime
    import hashlib

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    thread_id = hashlib.md5(f"{request.remote_addr}_{timestamp}".encode()).hexdigest()

    # Initialize the assistant handler
    assistant_handler = AssistantHandler(question, assistant_id)

    # TODO: Are we still using this? `assistant_handler._r = r`
    assistant_handler._r = r

    assistant_handler._FLASK_SSE = False  # Use Redis directly
    assistant_handler._py_thread_id = thread_id

    # Start a background thread to process the assistant response
    threading.Thread(
        target=assistant_handler.run,
        args=(thread_id,)
    ).start()

    # Return the thread ID to the client
    return jsonify({"thread_id": thread_id})


def stream_route(r):
    """Stream endpoint that uses Redis pub/sub for real-time updates."""
    channel = request.args.get('channel')
    if not channel:
        return Response("Channel parameter is required", status=400)

    # We'll listen for partial messages on `channel`
    # and for a final "complete" message on `channel + '_complete'`.
    primary_channel = channel
    complete_channel = f"{channel}_complete"

    def generate():
        pubsub = r.pubsub()
        # Subscribe to both channels
        pubsub.subscribe(primary_channel, complete_channel)

        # Send a content type header for SSE
        yield "Content-Type: text/event-stream\n\n"

        try:
            for message in pubsub.listen():
                # Redis pubsub returns various message types; we're interested in "message"
                if message['type'] == 'message':
                    raw_data = message['data']
                    if not raw_data:
                        continue

                    # Convert from bytes to string if necessary
                    data_str = raw_data.decode('utf-8')
                    this_channel = message['channel'].decode('utf-8')

                    # Check which channel triggered the event
                    if this_channel == primary_channel:
                        # This is our partial (streaming) content
                        # No explicit "event:" line => default event is "message"
                        yield f"data: {data_str}\n\n"

                    elif this_channel == complete_channel:
                        # This is the final message
                        # We'll send event: complete
                        yield "event: complete\n"
                        yield f"data: {data_str}\n\n"

                        # If you want to close out after final message:
                        # break
        except GeneratorExit:
            # Clean up when the client disconnects
            pubsub.unsubscribe()
            pubsub.close()

    return Response(generate(), mimetype='text/event-stream')
