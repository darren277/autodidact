""""""

assessment_generation_tool = {
    "type": "function",
    "function": {
        "name": "generate_practice_problem",
        "description": "Generate a practice problem for a given topic",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The subject topic for the practice problem",
                },
                "difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "Difficulty level of the problem",
                },
            },
            "required": ["topic"],
        },
    }
}
