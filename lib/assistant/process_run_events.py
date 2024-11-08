""""""
import time

from lib.assistant.handle_event import handle_event
from lib.assistant.initialize import logger, get_run_status, client


def process_run_events(initial_event_stream, thread_id, front_end_callback, tool_outputs=None):
    run_active, run_id = True, None
    event_stream = initial_event_stream
    while run_active:
        try:
            with event_stream as es:
                for event in es:
                    event_type = event.event
                    logger.debug(f"Received event: {event_type}")
                    if event_type == "thread.run.created" and run_id is None:
                        run_id = event.data.id
                    else:
                        if run_id is None:
                            logger.debug("-----> Run ID not obtained; cannot proceed.")
                            run_active = False
                            break
                    result, new_event_stream = handle_event(event, run_id, thread_id, front_end_callback)
                    if result == "switch_stream":
                        event_stream = new_event_stream
                        break
                    elif result == "stop":
                        run_active = False
                        break
                else:
                    if run_id:
                        run_status = get_run_status(thread_id, run_id)
                        if run_status in ["completed", "failed", "cancelled"]:
                            run_active = False
                        else:
                            time.sleep(1)
                            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                            stream = (client.beta.threads.runs.submit_tool_outputs_stream(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs))
                            try:
                                event_stream = run.events(stream=True)
                            except Exception as e:
                                logger.debug(f"------> Error re-initializing event stream: {e}")
                                run_active = False
                    else:
                        logger.debug("Run ID not obtained; cannot proceed.")
                        run_active = False
        except Exception as e:
            logger.debug(f"Error processing events: {e}")
            run_active = False
            break
