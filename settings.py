""""""
import logging
import os
from dotenv import load_dotenv

load_dotenv()

PORT = os.environ.get('PORT', 5000)

GPT_MODEL_ID=os.environ.get('GPT_MODEL_ID', 'gpt-4o')
GPT_ASSISTANT_NAME=os.environ.get('GPT_ASSISTANT_NAME', "Interactive Learning Companion")

SYSTEM_PROMPT=os.environ.get('SYSTEM_PROMPT', "You are a personal tutor specializing in mathematics and science. Provide clear, step-by-step explanations to help students understand concepts. When appropriate, use diagrams or examples to illustrate points.")

HOST='0.0.0.0'
DEBUG=True
ENABLE_CORS=True

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

LOG_LEVEL = os.environ.get('LOG_LEVEL', logging.DEBUG)


PG_HOST = os.environ.get('PG_HOST', 'localhost')
PG_PORT = os.environ.get('PG_PORT', 5432)
PG_USER = os.environ.get('PG_USER', 'myusername')
PG_PASS = os.environ.get('PG_PASS', 'mypassword')
PG_DB = os.environ.get('PG_DB', 'autodidact')
