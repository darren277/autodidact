""""""

content_rerieval_tool = {
    "type": "function",
    "function": {
        "name": "fetch_learning_material",
        "description": "Retrieve learning materials on a specific topic",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The subject topic to retrieve materials for, e.g., 'Pythagorean theorem'",
                },
                "material_type": {
                    "type": "string",
                    "enum": ["explanation", "example", "diagram"],
                    "description": "Type of material to retrieve",
                },
            },
            "required": ["topic"],
        },
    }
}
