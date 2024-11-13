""""""
from tests.ai_types.tools import FunctionTool

example_function_tools = [func1, func2, func3]

example_run = Run(
        id='run_SjOyYdWvnBuubfBmsbOFAt6h',
        assistant_id='asst_Gz3JQyRWZLsAdOt00a6jYnnN',
        cancelled_at=None,
        completed_at=None,
        created_at=1730761138,
        expires_at=1730761738,
        failed_at=None,
        incomplete_details=None,
        instructions=SYSTEM_PROMPT,
        last_error=None,
        max_completion_tokens=None,
        max_prompt_tokens=None,
        metadata={},
        model='gpt-4o-mini',
        object='thread.run',
        parallel_tool_calls=True,
        required_action=None,
        response_format='auto',
        started_at=None,
        status='queued',
        thread_id='thread_InASxxZgJUijrFRBa6UhRkZa',
        tool_choice='auto',
        #tools=[],
        tools=example_function_tools,
        truncation_strategy=TruncationStrategy(type='auto', last_messages=None),
        usage=None,
        temperature=1.0,
        top_p=1.0,
        tool_resources={'code_interpreter': {'file_ids': []}}
)


from settings import SYSTEM_PROMPT

#FunctionTool(function=FunctionDefinition(name='fetch_learning_material', description='Retrieve learning materials on a specific topic', parameters={'type': 'object', 'properties': {'topic': {'type': 'string', 'description': "The subject topic to retrieve materials for, e.g., 'Pythagorean theorem'# "}, 'material_type': {'type': 'string', 'enum': ['explanation', 'example', 'diagram'], 'description': 'Type of material to retrieve'}}, 'required': ['topic']}, strict=False), type='function'),
#FunctionTool(function=FunctionDefinition(name='generate_practice_problem', description='Generate a practice problem for a given topic', parameters={'type': 'object', 'properties': {'topic': {'type': 'string', 'description': 'The subject topic for the practice problem'}, 'difficulty': {'type': 'string', 'enum': ['easy', 'medium', 'hard'], 'description': 'Difficulty level of the problem'}}, 'required': ['topic']}, strict=False), type='function'),
#FunctionTool(function=FunctionDefinition(name='record_student_progress', description="Record and analyze the student's progress", parameters={'type': 'object', 'properties': {'student_id': {'type': 'string', 'description': 'Unique identifier for the student'}, 'topic': {'type': 'string', 'description': 'The subject topic the student is working on'}, 'performance': {'type': 'string', 'description': 'Performance data or scores'}}, 'required': ['student_id', 'topic', 'performance']}, strict=False), type='function')




ThreadRunCreated(data=example_run, event='thread.run.created')




Message(
    id='msg_9ozxQQidVCqC12YbhA6DYlkx',
    assistant_id='asst_KQhdZNSe270pnu0yjZ0CqLPd',
    attachments=[],
    completed_at=None,
    content=[TextContentBlock(
        text=Text(annotations=[], value='The total of 4052 and 3559 is **7611**.'),
        type='text'
    )],
    created_at=1730928685,
    incomplete_at=None,
    incomplete_details=None,
    metadata={},
    object='thread.message',
    role='assistant',
    run_id='run_BDf1Desms5TV38sR3gNNwZsT',
    status=None,
    thread_id='thread_dCCmStEMBxwqIiNOXBxCNVHa'
)

func1 = Function(arguments='{"topic": "quadratic equations", "material_type": "explanation"}', name='fetch_learning_material')
func2 = Function(arguments='{"topic": "quadratic equations", "material_type": "example"}', name='fetch_learning_material')
func3 = Function(arguments='{"topic": "quadratic equations", "material_type": "diagram"}', name='fetch_learning_material')

RequiredAction(
    submit_tool_outputs=RequiredActionSubmitToolOutputs(
        tool_calls=[
            RequiredActionFunctionToolCall(id='call_QG9UyOgN0CXFkEcsbeWfOH9h', function=func1, type='function'),
            RequiredActionFunctionToolCall(id='call_i17br4DbJtBS5zd2lIrypbFD', function=func2, type='function'),
            RequiredActionFunctionToolCall(id='call_h4tQ52B8fEh8GMyQg3ExZWNM', function=func3, type='function')
        ]
    ),
    type='submit_tool_outputs'
)


action_required = Run(
    id='run_oWZyTIqyDUPxsH3K8jrHrLkB',
    assistant_id='asst_xO9VVPMCTRzW8Q39NiUEShcp',
    cancelled_at=None,
    completed_at=None,
    created_at=1730829679,
    expires_at=1730830279,
    failed_at=None,
    incomplete_details=None,
    instructions='You are a personal tutor specializing in mathematics and science. Provide clear, step-by-step explanations to help students understand concepts. When appropriate, use diagrams or examples to illustrate points.',
    last_error=None,
    max_completion_tokens=None,
    max_prompt_tokens=None,
    metadata={},
    model='gpt-4o-mini',
    object='thread.run',
    parallel_tool_calls=True,
    required_action=example_required_action,
    response_format='auto',
    started_at=1730829680,
    status='requires_action',
    thread_id='thread_rJn1DI6qGt3ekDsEcG24qTQA',
    tool_choice='auto',
    tools=[
        FunctionTool(
            function=FunctionDefinition(
                name='fetch_learning_material',
                description='Retrieve learning materials on a specific topic',
                parameters={
                    'type': 'object',
                    'properties':
                        {
                            'topic': {'type': 'string', 'description': "The subject topic to retrieve materials for, e.g., 'Pythagorean theorem'"},
                            'material_type': {'type': 'string', 'enum': ['explanation', 'example', 'diagram'], 'description': 'Type of material to retrieve'}
                        },
                    'required': ['topic']
                },
                strict=False
            ),
            type='function'
        ),
        FunctionTool(
            function=FunctionDefinition(
                name='generate_practice_problem',
                description='Generate a practice problem for a given topic',
                parameters={
                    'type': 'object',
                    'properties':
                        {
                            'topic': {'type': 'string', 'description': 'The subject topic for the practice problem'},
                            'difficulty': {'type': 'string', 'enum': ['easy', 'medium', 'hard'], 'description': 'Difficulty level of the problem'}
                        },
                    'required': ['topic']
                },
                strict=False
            ),
            type='function'
        ),
        FunctionTool(
            function=FunctionDefinition(
                name='record_student_progress',
                description="Record and analyze the student's progress",
                parameters={'type': 'object', 'properties': {'student_id': {'type': 'string', 'description': 'Unique identifier for the student'}, 'topic': {'type': 'string', 'description': 'The subject topic the student is working on'}, 'performance': {'type': 'string', 'description': 'Performance data or scores'}}, 'required': ['student_id', 'topic', 'performance']},
                strict=False
            ),
            type='function'
        )
    ],
    truncation_strategy=TruncationStrategy(type='auto', last_messages=None),
    usage=None,
    temperature=1.0,
    top_p=1.0,
    tool_resources={'code_interpreter': {'file_ids': []}}
)




#thread.message.delta
MessageDeltaEvent(
    id='msg_5CzMTTr8e4qq2nIuCn1Ekzz2',
    delta=MessageDelta(
        content=[
            TextDeltaBlock(index=0, type='text', text=TextDelta(annotations=None, value=' factor'))
        ],
        role=None
    ),
    object='thread.message.delta'
)
#thread.message.delta
MessageDeltaEvent(
    id='msg_5CzMTTr8e4qq2nIuCn1Ekzz2',
    delta=MessageDelta(
        content=[
            TextDeltaBlock(index=0, type='text', text=TextDelta(annotations=None, value=')'))
        ],
        role=None
    ),
    object='thread.message.delta'
)
#thread.message.delta
MessageDeltaEvent(
    id='msg_5CzMTTr8e4qq2nIuCn1Ekzz2',
    delta=MessageDelta(
        content=[
            TextDeltaBlock(index=0, type='text', text=TextDelta(annotations=None, value='x'))
        ],
        role=None
    ),
    object='thread.message.delta'
)
#thread.message.delta
MessageDeltaEvent(
    id='msg_5CzMTTr8e4qq2nIuCn1Ekzz2',
    delta=MessageDelta(
        content=[
            TextDeltaBlock(index=0, type='text', text=TextDelta(annotations=None, value='left'))
        ],
        role=None
    ),
    object='thread.message.delta'
)
#thread.message.delta
MessageDeltaEvent(
    id='msg_5CzMTTr8e4qq2nIuCn1Ekzz2',
    delta=MessageDelta(
        content=[
            TextDeltaBlock(index=0, type='text', text=TextDelta(annotations=None, value=' feel'))
        ],
        role=None
    ),
    object='thread.message.delta'
)




## run failed... ##

step_details = ToolCallsStepDetails(
    tool_calls=[
        FunctionToolCall(
            id='call_ZhlisBFLvicahNad9WneTDWZ',
            function=Function(arguments='{"topic": "quadratic equations", "material_type": "explanation"}', name='fetch_learning_material', output=None),
            type='function'
        ),
        FunctionToolCall(
            id='call_h5c52AfpUGfcPvso1Xoshi0j',
            function=Function(arguments='{"topic": "quadratic equations", "material_type": "diagram"}', name='fetch_learning_material', output=None),
            type='function')
    ],
    type='tool_calls'
)


RunStep(
    id='step_Z2oSPW3NAOzIs2YXgr9VKh8j',
    assistant_id='asst_Zs1yQbvMBbSvu1l3ZoPyFxAO',
    cancelled_at=None,
    completed_at=None,
    created_at=1730913862,
    expired_at=None,
    failed_at=1730913883,
    last_error=LastError(code='server_error', message='Sorry, something went wrong.'),
    metadata=None,
    object='thread.run.step',
    run_id='run_Xe1VgEJmK9jhA507DTTqTd6h',
    status='failed',
    step_details=step_details,
    thread_id='thread_q3FLsE9J11Cvy9wo96vOJAdl',
    type='tool_calls',
    usage=Usage(completion_tokens=62, prompt_tokens=462, total_tokens=524),
    expires_at=1730914461
)

RunStepDeltaEvent(
    id='step_NMfuIYCT3lUt40ZHJ51EJPkd',
    delta=RunStepDelta(
        step_details=ToolCallDeltaObject(
            type='tool_calls',
            tool_calls=[
                FunctionToolCallDelta(
                    index=0,
                    type='function',
                    id='call_ceiIWOm9G8WMjR9RUucoXj0R',
                    function=Function(
                        arguments='',
                        name='fetch_learning_material',
                        output=None
                    )
                )
            ]
        )
    ),
    object='thread.run.step.delta'
)
# delta.step_details.tool_calls

RunStepDeltaEvent(
    id='step_j5OLyZBc5jbL2djhSNR4qIpz',
    delta=RunStepDelta(
        step_details=ToolCallDeltaObject(
            type='tool_calls',
            tool_calls=[
                FunctionToolCallDelta(index=1, type='function', id=None, function=Function(arguments='ial_ty', name=None, output=None))
            ]
        )
    ),
    object='thread.run.step.delta'
)
# delta.step_details.tool_calls
