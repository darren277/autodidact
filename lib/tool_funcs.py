""""""
from lib.funcs.main import fetch_learning_material, generate_practice_problem, record_student_progress

tool_funcs_dict = {
    'fetch_learning_material': lambda kwargs: fetch_learning_material(**kwargs),
    'generate_practice_problem': lambda kwargs: generate_practice_problem(**kwargs),
    'record_student_progress': lambda kwargs: record_student_progress(**kwargs),
    'addition': lambda x, y: x + y,
    'square_a_number': lambda x: x ** 2
}

def process_tool_func(function_name: str, *args, **kwargs) -> str:
    return str(tool_funcs_dict.get(function_name, lambda *args, **kwargs: "Function not recognized.")(*args, **kwargs))
