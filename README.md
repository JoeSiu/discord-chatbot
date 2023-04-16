# Discord ChatBot

## Description

The Discord ChatBot is a Python-based chatbot that supports following:

- [Poe](https://poe.com/) bots, including `Sage`, `GPT-4`, `Claude+`, `Claude-instant`, `ChatGPT`, `Dragonfly` and custom bots (via [Unoffical API](https://github.com/ading2210/poe-api))

- All [Hugging Face conversational models](https://huggingface.co/models?pipeline_tag=conversational)

## Demo

![discord-chatbot](https://user-images.githubusercontent.com/38518793/230790942-98d55cb7-3fb3-4442-92b2-9b697ad086d0.gif)

## Installation Instructions

To run the Discord ChatBot, follow these steps:

### Setup

1. Clone this repository using Git.
2. Duplicate the `.env.example` file and rename it to `.env`. Replace each key with the corresponding values.
3. Go to [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
4. Create a bot and copy its token.
5. Paste the token into the `DISCORD_TOKEN` field in the `.env` file.

#### Environment Variables

| Env variables      | Description                                                                                                                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DISCORD_TOKEN      | Discord token, obtained from [https://discord.com/developers/applications](https://discord.com/developers/applications).                                                                                                   |
| POE_TOKEN          | Poe token, should be the browser cookie for [https://poe.com](https://poe.com/), refer to [poe-api](https://github.com/ading2210/poe-api) repository for more details. Leave empty if you don't intend to use the Poe bot. |
| POE_MODEL          | Default Poe bot (name), e.g., `Sage`, `GPT-4`, `Claude+`, `Claude-instant`, `ChatGPT`, `Dragonfly`. Leave empty if you don't intend to use the Poe bot.                                                                    |
| POE_PROXY          | The default proxy. Leave empty if you don't intend to use the Poe bot or want to skip using a proxy.                                                                                                                       |
| HUGGING_FACE_TOKEN | Hugging Face token, obtained from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens). Leave empty if you don't intend to use the Hugging Face bot.                                           |
| HUGGING_FACE_MODEL | Default Hugging Face model, refer to [Hugging Face conversational models](https://huggingface.co/models?pipeline_tag=conversational). Leave empty if you don't intend to use the Hugging Face bot.                         |
| DEBUG              | Whether to use debug view.                                                                                                                                                                                                 |

#### Poe

To use the Poe bot, follow the steps below:

1. Refer to [poe-api guide](https://github.com/ading2210/poe-api#finding-your-token) to obtain your token.
2. Update the `POE_TOKEN` field in the `.env` file.
3. Set the `POE_MODEL` field to the desired model (e.g., `ChatGPT`).
4. Optionally, set the `POE_PROXY` field for proxy settings.

#### Hugging Face

To use the Hugging Face bot, follow the steps below:

1. Obtain your Hugging Face API token from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. Set the `HUGGING_FACE_MODEL` field to the desired model. (Find the model from [https://huggingface.co/models?pipeline_tag=conversational](https://huggingface.co/models?pipeline_tag=conversational), then copy the model name, e.g., `facebook/blenderbot-3B`).

### Run the program

#### CLI

1. Make sure you have Python3 installed.
2. Run `pip install -r requirements.txt` to install the required dependencies, using python virtual environment is recommended.
3. Run `python main.py` to start the bot.

##### Available command arguments

You can also use the following command arguments:

| Arugments                      | Description                                              | Options               |
| ------------------------------ | -------------------------------------------------------- | --------------------- |
| `--bot [str]`                  | Select the chatbot to use.                               | `poe`, `hugging-face` |
| `--model [str]`                | Select the chatbot model to use.                         | Depends on bot        |
| `--channel-monitor-mode [str]` | Select the channel monitor mode.                         | `all`, `none`         |
| `--enable-name-prefix [bool]`  | Enable or disable prefixing user names to chat messages. | `True`, `False`       |

#### Docker (Work in Progress)

Make sure you have python and docker installed

1. Make sure you have Docker installed.
2. run `docker-compose build` to build the docker image.
3. run `docker-compose up -d` to start the container.

## Usage

### Discord commands

| Command                              | Description                                                                                                                                             | Options               |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| `/send [str]`                        | Send a message to the chatbot. This command can bypass Discord's message limit for non-nitro users and allows messages up to 6000 characters in length. |                       |
| `/clear-context`                     | Clear the current context of the chatbot.                                                                                                               |                       |
| `/get-bot`                           | Returns the current bot being used.                                                                                                                     |                       |
| `/change-bot [str]`                  | Changes the current bot being used. If an invalid bot is specified, the available bot names will be shown.                                              | `poe`, `hugging-face` |
| `/reset-bot`                         | Resets the current bot to the default bot specified in .env.                                                                                            |                       |
| `/get-model`                         | Returns the current chatbot model being used.                                                                                                           |                       |
| `/change-model [str]`                | Changes the current chatbot model being used. If an invalid model is specified, the available model names will be shown.                                | Depends on the bot    |
| `/reset-model`                       | Resets the current chatbot model to the default model specified in .env.                                                                                |                       |
| `/change-token [str]`                | Changes the API token for the chatbot.                                                                                                                  |                       |
| `/reset-token`                       | Resets the API token for the chatbot to the default token specified in .env.                                                                            |                       |
| `/enable-channel-monitoring`         | Enables monitoring of the current channel, will add the current channel to whitelist if `channel-monitor-mode` is set to `none`.                        |                       |
| `/disable-channel-monitoring`        | Disable monitoring of the current channel.                                                                                                              |                       |
| `/get-channel-whitelist`             | Returns the channel whitelist.                                                                                                                          |                       |
| `/get-channel-blacklist`             | Returns the channel blacklist.                                                                                                                          |                       |
| `/get-channel-monitor-mode`          | Returns the current monitoring mode.                                                                                                                    |                       |
| `/change-channel-monitor-mode [str]` | Changes the current monitoring mode. If an invalid mode is specified, the available modes will be shown.                                                | `all`, `none`         |
| `/enable-name-prefix`                | Enables prefixing the chat messages with the username or nickname.                                                                                      |                       |
| `/disable-name-prefix`               | Disables prefixing the chat messages with the username or nickname.                                                                                     |                       |
| `/register-nickname [str]`           | Registers or updates a nickname.                                                                                                                        |                       |
| `/unregister-nickname`               | Unregisters a nickname if it is registered.                                                                                                             |                       |
| `/get-nickname`                      | Returns the registered nickname if there is one.                                                                                                        |                       |

- You can also use `$ignore` at the beginning of a message to instruct the bot to ignore that message.
- In channel monitor mode, setting it to `all` will cause the bot to reply to messages in all channels, except for those in the blacklist. Setting it to `none` will prevent the bot from replying to messages in any channel, except for those in the whitelist.
- When name prefix is enabled, the bot will automatically add the Discord username or nickname (if registered via the `/register-nickname` command) of the message author to the front of the message. For example, the message `hello` will become `Joe: hello` when sent to the bot. This feature is useful for multi-person conversations, especially when giving the bot a prompt.

## Limitation

- Currently, the bot has only been tested on a single server and in direct messages.
- The bot is a single instance only, which means that any messages or commands sent in direct messages or different channels will be treated as if they came from the same source.

## Note

- This is just a simple holiday project, might not update in the future. 🙃
