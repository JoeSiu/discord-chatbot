# Discord ChatBot

The Discord ChatBot is a Python-based chatbot that supports following:

- [Poe](https://poe.com/) bots, including `Sage`, `GPT-4`, `Claude+`, `Claude-instant`, `ChatGPT`, `Dragonfly` (via [Unoffical API](https://github.com/ading2210/poe-api))

- All [Hugging Face](https://huggingface.co/models?pipeline_tag=conversational) conversational models

## Installation

To run the Discord ChatBot, follow these steps:

### Prerequites

1. Clone this repository using Git.

2. Duplicate the .env.template file and rename it to .env. Replace each key with the corresponding values.

| Env variables      | Description                                                                                                                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DISCORD_TOKEN      | Discord token, obtained from [https://discord.com/developers/applications](https://discord.com/developers/applications).                                                                                                   |
| POE_TOKEN          | Poe token, should be the browser cookie for [https://poe.com](https://poe.com/), refer to [poe-api](https://github.com/ading2210/poe-api) repository for more details. Leave empty if you don't intend to use the Poe bot. |
| POE_MODEL          | Default Poe bot (name), e.g., `Sage`, `GPT-4`, `Claude+`, `Claude-instant`, `ChatGPT`, `Dragonfly`. Leave empty if you don't intend to use the Poe bot.                                                                    |
| POE_PROXY          | The default proxy. Leave empty if you don't intend to use the Poe bot or want to skip using a proxy.                                                                                                                       |
| HUGGING_FACE_TOKEN | Hugging Face token, obtained from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens). Leave empty if you don't intend to use the Hugging Face bot.                                           |
| HUGGING_FACE_MODEL | Default Hugging Face model, refer to [Hugging Face conversational models](https://huggingface.co/models?pipeline_tag=conversational). Leave empty if you don't intend to use the Hugging Face bot.                         |
| DEBUG              | Whether to use debug view.                                                                                                                                                                                                 |

#### CLI

1. Make sure you have Python installed.

2. Run `pip install -r requirements.txt` to install the required dependencies., using python virtual environment is recommended.

3. Run `python main.py` to start the bot.

##### Available command arguments

You can also use the following command arguments:

| Arugments                | Description                      |
| ------------------------ | -------------------------------- |
| `--bot`                  | 'Select the chatbot to use.      |
| `--channel-monitor-mode` | Select the channel monitor mode. |
| `--model`                | Select the chatbot model to use. |

#### Docker (Work in Progress)

Make sure you have python and docker installed

1. Make sure you have Python and Docker installed.

2. Clone this repository using Git.

3. run `docker-compose build` to build the docker image.

4. run `docker-compose up -d` to start the container.

## Usage

Only tested on a single server and direct messages.

### Discord commands

| Command                        | Description |
| ------------------------------ | ----------- |
| `/send`                        |             |
| `/clear-context`               |             |
| `/get-bot`                     |             |
| `/change-bot`                  |             |
| `/reset-bot`                   |             |
| `/get-model`                   |             |
| `/change-model`                |             |
| `/reset-model`                 |             |
| `/change-token`                |             |
| `/reset-token`                 |             |
| `/enable-channel-monitoring`   |             |
| `/disable-channel-monitoring`  |             |
| `/get-channel-whitelist`       |             |
| `/get-channel-blacklist`       |             |
| `/get-channel-monitor-mode`    |             |
| `/change-channel-monitor-mode` |             |

---

<sub>First time making a discord bot so please expect many bugs 🙃</sub>
