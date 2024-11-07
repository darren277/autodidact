""""""
from lib.funcs.main import fetch_learning_material, generate_practice_problem, record_student_progress

from lib.tools.assessment_generation import assessment_generation_tool
from lib.tools.content_retrieval import content_rerieval_tool
from lib.tools.progress_tracking import progress_tracking_tool

tool_funcs_dict = {
    'fetch_learning_material': lambda kwargs: fetch_learning_material(**kwargs),
    'generate_practice_problem': lambda kwargs: generate_practice_problem(**kwargs),
    'record_student_progress': lambda kwargs: record_student_progress(**kwargs),
    'addition': lambda x, y: x + y# Tool call ID: call_zMJcq1Wcl0UZ78lRozw5Qvwg, Function name: addition, Arguments: {"x":4052,"y":3559}
    # args = json.loads(arguments)
    #                     logger.debug(f"ADDITION ARGS: {args}")
    #                     result = str(add_func(args['x'], args['y']))
}

def process_tool_func(function_name: str, *args, **kwargs) -> str:
    # Handle this case inside of each function: if not result: result = "No output generated for this tool call."

    # Error submitting tool outputs: Error code: 400 - {'error': {'message': "Invalid type for 'tool_outputs[0].output': expected a string, but got an integer instead.", 'type': 'invalid_request_error', 'param': 'tool_outputs[0].output', 'code': 'invalid_type'}}

    return str(tool_funcs_dict.get(function_name, lambda *args, **kwargs: "Function not recognized.")(*args, **kwargs))
