""""""
from lib.assistant.initialize import *


def submit_tool_outputs(tool_calls, run_id, thread_id):
    tool_outputs = []
    for tool_call in tool_calls:
        tool_call_id, function_name, arguments = tool_call.id, tool_call.function.name, tool_call.function.arguments
        output = process_tool_function(function_name, arguments)
        tool_outputs.append({"tool_call_id": tool_call_id, "output": output})

    new_event_stream = client.beta.threads.runs.submit_tool_outputs_stream(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)
    logger.debug("Submitted tool outputs:", tool_outputs)
    return new_event_stream


def process_tool_function(function_name, arguments):
    args = json.loads(arguments)
    if function_name == "add_numbers":
        logger.debug("________________________________ADD NUMBERS____________________________________")
        a = args.get("a", 0)
        b = args.get("b", 0)
        result = a + b
        return json.dumps({"result": result})
    if function_name == "multiply_numbers":
        logger.debug("________________________________MULTIPLY NUMBERS____________________________________")
        a = args.get("a", 0)
        b = args.get("b", 0)
        result = a * b
        return json.dumps({"result": result})
    else:
        return json.dumps({"error": f"Function '{function_name}' not implemented."})

