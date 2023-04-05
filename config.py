from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Discord and Hugging Face tokens
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")
HUGGING_FACE_MODEL = os.getenv("HUGGING_FACE_MODEL")
DEBUG = bool(os.getenv("DEBUG"))
