from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Discord and Hugging Face tokens
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_GUILD_ID = int(os.getenv("SERVER_GUILD_ID"))
HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")
HUGGING_FACE_MODEL = os.getenv("HUGGING_FACE_MODEL")
DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')
