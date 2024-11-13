""""""
from typing import List


class FunctionDefinition:
    def __init__(self, name: str, description: str, parameters: dict, strict: bool):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.strict = strict

class FunctionTool:
    def __init__(self, function: FunctionDefinition, type: str):
        self.function = function
        self.type = type

class RequiredActionFunctionToolCall:
    def __init__(self, id: str, function: FunctionDefinition, type: str):
        self.id = id
        self.function = function
        self.type = type

class RequiredActionSubmitToolOutputs:
    def __init__(self, tool_calls: List[RequiredActionFunctionToolCall]):
        self.tool_calls = tool_calls



class RequiredAction:
    def __init__(self, submit_tool_outputs: RequiredActionSubmitToolOutputs, type: str):
        self.submit_tool_outputs = submit_tool_outputs
        self.type = type
