import json
import os
from dotenv import load_dotenv

# Constants
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "nicknames": {},
    "channel_whitelist": [],
    "channel_blacklist": []
}

# Initialize variables
data = {}

# Load environment variables from .env file
load_dotenv()


def load_config():
    """
    Load configuration from JSON file
    """
    global data
    # Check if the config file exists
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return True
    else:
        # If the config file doesn't exist, create a new one with default values
        reset_config()
        return False


def save_config():
    """
    Save configuration to JSON file
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)


def reset_config():
    """
    Reset configuration to default
    """
    global data
    data = DEFAULT_CONFIG
    save_config()


# Load Discord and Hugging Face tokens from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
HUGGING_FACE_MODEL = os.getenv("HUGGING_FACE_MODEL")

# Load POE settings from environment variables
POE_TOKEN = os.getenv("POE_TOKEN")
POE_MODEL = os.getenv("POE_MODEL")
POE_PROXY = os.getenv("POE_PROXY")

# Load debug mode setting from environment variables
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "t")
