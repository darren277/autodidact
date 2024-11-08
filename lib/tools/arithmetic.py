"""
These tools are very simple ones meant simply for testing.
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Adds two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_numbers",
            "description": "Multiplies two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"},
                },
                "required": ["a", "b"],
            },
        },
    }
]


tools1 = [
    {
"type": "function",
    "function": {
        "name": "addition",
        "description": "Add two numbers together",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {
                    "type": "number",
                    "description": "The X value to be added.",
                },
                "y": {
                    "type": "number",
                    "description": "The Y value to be added",
                },
            },
            "required": ["x", "y"]
        }
    }
    }
]
