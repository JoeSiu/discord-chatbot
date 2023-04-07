from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Discord and Hugging Face tokens
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
HUGGING_FACE_MODEL = os.getenv("HUGGING_FACE_MODEL")
POE_TOKEN = os.getenv("POE_TOKEN")
POE_MODEL = os.getenv("POE_MODEL")
POE_PROXY = os.getenv("POE_PROXY")
DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')
