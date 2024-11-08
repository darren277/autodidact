""""""

def handle_event(event, run_id, thread_id, front_end_callback):
    event_type = event.event
    if event_type == "thread.run.started":
        return "continue", None
    elif event_type == "thread.message.delta":
        content = event.data.delta.content
        if content: front_end_callback(content)
        return "continue", None
    elif event_type == "thread.run.requires_action":
        tool_calls = event.data.required_action.submit_tool_outputs.tool_calls
        new_event_stream = submit_tool_outputs(tool_calls, run_id, thread_id)
        return "switch_stream", new_event_stream
    elif event_type == "thread.run.completed":
        logger.debug("Run completed successfully.")
        return "stop", None
    elif event_type == "thread.run.failed":
        logger.debug(f"Run failed with error: {event.data.last_error}")
        return "stop", None
    else:
        logger.debug(f"Unhandled event type: {event_type}")
        return "continue", None

