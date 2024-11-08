""""""

progress_tracking_tool = {
    "type": "function",
    "function": {
        "name": "record_student_progress",
        "description": "Record and analyze the student's progress",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Unique identifier for the student",
                },
                "topic": {
                    "type": "string",
                    "description": "The subject topic the student is working on",
                },
                "performance": {
                    "type": "string",
                    "description": "Performance data or scores",
                },
            },
            "required": ["student_id", "topic", "performance"],
        },
    }
}
