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

Begin dialogue now.
"""

# I don't think these stage directions are going to work at this time:
# [Include brief actions or stage directions in brackets occasionally, e.g., [laughs], [scratches head], [points at map].]

def construct_dramatized_narrative_prompt(char1_name: str, char1_description: str, char2_name: str, char2_description: str, input_text: str) -> str:
    return DRAMATIZED_NARRATIVE_PROMPT.format(char1_name=char1_name, char1_description=char1_description, char2_name=char2_name, char2_description=char2_description, input_text=input_text)


# Idea: Essentially the same idea but for converting your structured notes into a fun, engaging presentation.

STRUCTURED_NOTES_PRESENTATION_PROMPT = """
Objective:
Transform the provided structured notes into an engaging, multi-character lecture. Each note card should be presented by a designated character based on the note's category, as defined below. Characters should maintain distinct, realistic personalities and seamlessly introduce their notes with brief context or smooth transitions.

Characters and Categories:

Main Narrator (General notes - part.main without special categories): Thoughtful, clear, and engaging teacher, who provides foundational context and gently guides the overall lecture flow.

Historian (COLORS.EVENT): Enthusiastic, detail-oriented, and passionate about historical events, providing vivid descriptions and historical context.

Innovator (COLORS.IDEA): Curious, forward-thinking, and insightful speaker who connects ideas to their broader implications, often suggesting future possibilities or intriguing hypotheses.

Lecture Structure:

Begin with a brief introduction by the Main Narrator, establishing the overall topic and its significance.

Transition fluidly between characters, each clearly identified, providing natural segues between notes.

End the lecture with the Main Narrator providing a concise, memorable summary, reinforcing key points covered by all speakers.

Educational Psychology Principles to Follow:

Contextual Embedding: Each character should naturally link their note to previously mentioned ideas or events, helping learners build connections and deepen comprehension.

Variety and Personality: Different character styles maintain learner engagement and attention.

Recap and Reinforcement: Brief summaries or callbacks to key ideas at natural intervals aid retention.

Concrete Examples: Characters enhance notes with clear examples, analogies, or brief anecdotes appropriate to their personas.

Structured Notes Input:
{structured_notes}

Output Format:
Narrator: [Introduction providing overview and setting the stage for the lecture.]
Historian: [Delivers event-related notes, vividly and clearly.]
Innovator: [Shares ideas or implications, adding thoughtful context and insights.]
Narrator: [Smoothly transitions or connects ideas, ensuring coherence.]
[Continue alternating speakers according to note categories until complete.]
Narrator: [Provides a concise summary, recapping and reinforcing key points.]

Begin Lecture Now.
"""

def construct_structured_notes_presentation_prompt(structured_notes: str) -> str:
    return STRUCTURED_NOTES_PRESENTATION_PROMPT.format(structured_notes=structured_notes)
