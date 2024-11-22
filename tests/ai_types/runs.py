""""""
from typing import List, Optional, Dict, Any


class Run:
    def __init__(self, id: str, assistant_id: str, cancelled_at: Optional[int], completed_at: Optional[int], created_at: int, expires_at: int, failed_at: Optional[int], incomplete_details: Optional[IncompleteDetails], instructions: str, last_error: Optional[LastError], max_completion_tokens: Optional[int], max_prompt_tokens: Optional[int], metadata: Dict[str, Any], model: str, object: str, parallel_tool_calls: bool, required_action: Optional[RequiredAction], response_format: str, started_at: Optional[int], status: str, thread_id: str, tool_choice: str, tools: List[FunctionTool], truncation_strategy: TruncationStrategy, usage: Optional[Usage], temperature: float, top_p: float, tool_resources: Dict[str, Any]):
        self.id = id
        self.assistant_id = assistant_id
        self.cancelled_at = cancelled_at
        self.completed_at = completed_at
        self.created_at = created_at
        self.expires_at = expires_at
        self.failed_at = failed_at
        self.incomplete_details = incomplete_details
        self.instructions = instructions
        self.last_error = last_error
        self.max_completion_tokens = max_completion_tokens
        self.max_prompt_tokens = max_prompt_tokens
        self.metadata = metadata
        self.model = model
        self.object = object
        self.parallel_tool_calls = parallel_tool_calls
        self.required_action = required_action
        self.response_format = response_format
        self.started_at = started_at
        self.status = status
        self.thread_id = thread_id
        self.tool_choice = tool_choice
        self.tools = tools
        self.truncation_strategy = truncation_strategy
        self.usage = usage
        self.temperature = temperature
        self.top_p = top_p
        self.tool_resources = tool_resources


class ThreadRunCreated:
    # <class 'openai.types.beta.assistant_stream_event.ThreadRunCreated'>
    def __init__(self, data: Run, event: str):
        self.data = data
        self.event = event
