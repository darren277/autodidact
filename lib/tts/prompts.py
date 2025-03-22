""""""

# Idea: Add a page for taking in either an article or unstructured notes and turning it into a fun narration with multiple random characters.

DRAMATIZED_NARRATIVE_PROMPT = """
Objective:
Convert the provided text into an entertaining and educational dialogue between {char1_name} and {char2_name}. Each character must stay true to their description provided below, engaging with distinct personalities and humor.

Educational Psychology Principles to follow:
* Self-Explanation Effect: Characters explain concepts back and forth, questioning each other to clarify ideas and deepen understanding.
* Humor and Novelty: Incorporate playful banter and unexpected analogies, keeping the conversation fun, quirky, and memorable.
* Spaced Repetition: Revisit the main points briefly at the start, middle, and end of the dialogue.
* Elaboration: Characters relate concepts to vivid scenarios from their unique backgrounds to enhance understanding and retention.
* Narrative Engagement: Weave a mini-story or scenario that naturally motivates the dialogue (e.g., a mystery, an adventure, or a misunderstanding they're trying to resolve together).

Characters:
{char1_name}: {char1_description}
{char2_name}: {char2_description}

Input Text:
{input_text}

Dialogue Format:
{char1_name}: "Dialogue line."
{char2_name}: "Dialogue line."
[Include brief actions or stage directions in brackets occasionally, e.g., [laughs], [scratches head], [points at map].]

Begin dialogue now.
"""

def construct_dramatized_narrative_prompt(char1_name: str, char1_description: str, char2_name: str, char2_description: str, input_text: str) -> str:
    return DRAMATIZED_NARRATIVE_PROMPT.format(char1_name=char1_name, char1_description=char1_description, char2_name=char2_name, char2_description=char2_description, input_text=input_text)

