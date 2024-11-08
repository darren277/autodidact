""""""

full_message = ""


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

def main():
    from lib.tools.arithmetic import tools
    prompt = "Add 1234 and 5678 then multiply by 2."
    assistant_id = "asst_X0dIT6aOTHFQgJNE923sjv8E"
    event_stream, thread_id = start_assistant_run(prompt, assistant_id, tools)
    process_run_events(event_stream, thread_id, front_end_callback)

    logger.debug("Full message:", full_message)


if __name__ == "__main__":
    main()
