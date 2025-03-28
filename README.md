# autodidact

## Description

You are the teacher and the student. An LLM enriched learning platform for designing lesson plans for others or for yourself.

An LLM rich web app built in Python using Flask, Flask-SSE, Redis, and the OpenAI API to facilitate self-education outcomes.

## How to Use

On Windows, install `Make` if you don't already have it.

Also, install the Python package `waitress` (`pip install waitress`).

Then, simply enter `make w` to start.

### Environment Variables

At the very least, you will need the following environment variables:
```shell
OPENAI_API_KEY=...
```

There are many more optional environment variables (see `settings.py`).

## Notes

### TTS

#### Stage Directions

The first iteration of each of the special prompts included instructions for including stage directions to the narrating / conversing personas.

This is a cool idea, in principle, to add even more depth to the experience.

However, it does not seem to be feasible just yet as the narration will include all included text.

For now, I will be removing any instruction to provide such details, but it may be worth exploring a way to somehow incorporate them.

For example, perhaps they can be included somehow into the `instructions` parameter.

Here is one example of what they looked like with the initial prompts:

```
Main Narrator:  Welcome, everyone, to our exploration of a fascinating topic
Historian:  (Enthusiastically takes the stage) Picture this
Innovator:  (Steps forward with a twinkle of curiosity in their eye) Building on our historian's brilliant insights, let's fast-forward just a bit. Once the lorem community unlocked the secrets of ipsum, they began cultivating it in vast quantities. But here's a question that invites our imagination
Main Narrator:  (Interjects to connect the threads) Thank you both for those vivid descriptions and thought-provoking ideas. Indeed, it's interesting to consider how a discovery turns into widespread cultivation�and how this simple process might lead to broader, unforeseen impacts. This naturally brings us to an important reflection point in our learning journey.
Historian:  (Nods and returns to the stage) A critical example to ponder
Innovator:  (Chimes in with zeal) Exactly! And every event invites us to think about the ripple effects of innovation. How might the endeavors initiated by the lorems inspire the next generations? We can liken it to turning a page in a book, revealing new adventures and knowledge ripe for exploration. Let's continue to picture the uncharted map of possibilities as we reflect on future implications.
Main Narrator:  (Summarizes with warmth) Today, we've explored an era and an idea that continues to inspire. From the monumental discovery of ipsum in 1967 to its cultivation and potential future impacts, each piece of this narrative is a testament to the power of discovery and innovation. Remember, these moments are not isolated�they're interconnected, painting a richer picture of progress. Thank you for joining us on this engaging journey through history and ideas. Let these thoughts simmer as we step into future explorations together!
```
