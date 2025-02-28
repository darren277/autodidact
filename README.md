# autodidact

## Description

An LLM web app built in Python using Flask, Flask-SSE, Redis, and the OpenAI API to facilitate self-education outcomes.

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
