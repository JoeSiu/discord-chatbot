import logging
import logging.handlers
import sys
import argparse
import discord
from discord import app_commands
import config

from enum import Enum

from chatbots.hugging_face_chatbot import HuggingFaceChatBot
from chatbots.poe_chatbot import PoeChatBot

# Setup logger
# Remove root logger stream output
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler):
        logging.getLogger().removeHandler(handler)

discord.utils.setup_logging(level=logging.INFO)
logger = logging.getLogger('discord')

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(
    '[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Create Discord client with appropriate intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Create command tree for Discord slash commands
tree = app_commands.CommandTree(client)

# Initialize chatbot object
chatbot = None


class BotType(Enum):
    POE = "poe"
    HUGGING_FACE = "hugging-face"


class ChannelMonitorMode(Enum):
    NONE = "none"
    ALL = "all"


class QueryStatus(Enum):
    SUCCESS = 0
    QUERY_ATTRIBUTE_ERROR = 2
    UNKNOWN_QUERY_ERROR = 1
    EMPTY_RESPONSE_ERROR = 3
    UNKNOWN_RESPONSE_ERROR = 4


# Nickname list
nicknames = {}

# Initialize channel whitelist and blacklist
channel_whitelist = []
channel_blacklist = []

# Current bot
current_bot = BotType.POE

# Current monitor mode
current_channel_monitor_mode = ChannelMonitorMode.ALL

# Current name prefix mode
current_name_prefix_mode = True


@tree.command(name="send", description="Send a message to the bot")
async def send(interaction, user_input: str):
    """
    Command to send a message to the current chatbot.
    """
    MAX_CHARS_PER_EMBED = 4096
    MAX_EMBEDS_PER_MESSAGE = 10

    try:
        # Defer sending message as query takes time
        await interaction.response.defer()

        preview = user_input
        # Split message into multiple embeds if necessary
        if len(preview) <= MAX_CHARS_PER_EMBED:
            embed = discord.Embed(description=preview)
            await interaction.followup.send(embed=embed)
        else:
            embeds = []
            while preview:
                chunk = preview[:MAX_CHARS_PER_EMBED]
                preview = preview[MAX_CHARS_PER_EMBED:]
                embed = discord.Embed(description=chunk)
                embeds.append(embed)
            # Send a list of embeds as separate messages, respecting Discord's character and embed limits.
            for i in range(0, len(embeds), MAX_EMBEDS_PER_MESSAGE):
                # Send up to MAX_EMBEDS_PER_MESSAGE embeds in a single message
                message_embeds = embeds[i:i + MAX_EMBEDS_PER_MESSAGE]
                await interaction.followup.send(embeds=message_embeds)

        async with interaction.channel.typing():
            # Add name prefix
            if current_name_prefix_mode:
                author_name = nicknames.get(
                    interaction.user.name, interaction.user.name)
                user_input = add_prefix_to_message(
                    f"{user_input}: ", author_name)

            logger.info(
                f"Input from {interaction.user.name} (via /send): {user_input}")

            status, response = await query(user_input)

            response = format_response_based_on_status(response, status)

            await interaction.followup.send(content=response)
    except Exception as e:
        logger.exception(f"change_bot error:  {type(e).__name__} - {e}")
        await interaction.followup.send(f"> Sorry, an error occured while trying to send the message.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="get-bot", description="Get the current bot")
async def get_bot(interaction):
    """
    Command to get the current chatbot.
    """
    try:
        bot_name = get_bot()
        message = f"> The current chatbot is: `{bot_name}`."
        logger.info(message)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.exception(f"get_bot error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"> Sorry, an error occured while trying to get bot.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="change-bot", description="Change the current bot")
async def change_bot(interaction, bot_name: str):
    """
    Command to change the current chatbot.
    """
    try:

        # Defer sending message as changing bot takes time
        await interaction.response.defer()

        success = change_bot(bot_name)

        if success:
            message = f"> Bot has been changed to: `{bot_name}`."
        else:
            bots = ", ".join([bot.value for bot in BotType])
            message = f"> Bot `{bot_name}` is invalid, available bot: {bots}."

        logger.info(message)
        await interaction.followup.send(message)
    except Exception as e:
        logger.exception(f"change_bot error:  {type(e).__name__} - {e}")
        await interaction.followup.send(f"> Sorry, an error occured while trying to change bot.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="reset-bot", description="Reset the current bot")
async def reset_bot(interaction):
    """
    Command to change the reset chatbot.
    """
    try:

        # Defer sending message as changing bot takes time
        await interaction.response.defer()

        success = change_bot(current_bot)

        if success:
            message = f"> Bot has been reset."
        else:
            message = f"> Fail to reset bot, please try again."

        logger.info(message)
        await interaction.followup.send(message)
    except Exception as e:
        logger.exception(f"reset_bot error:  {type(e).__name__} - {e}")
        await interaction.followup.send(f"> Sorry, an error occured while trying to reset bot.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="get-model", description="Get the current chatbot model")
async def get_model(interaction):
    """
    Command to get the current chatbot model.
    """
    try:
        model_name = chatbot.get_model()
        message = f"> The current chatbot model is: `{model_name}`."
        logger.info(message)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.exception(f"get_model error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"> Sorry, an error occured while trying to get model.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="change-model", description="Change the chatbot model")
async def change_model(interaction, model_name: str):
    """
    Command to change the chatbot model.
    """
    try:
        success = chatbot.change_model(model_name)
        if success:
            message = f"Model has been changed to: `{model_name}`."
        else:
            if current_bot == BotType.POE:
                available_models = ", ".join(
                    [f"`{value}`" for key, value in chatbot.get_available_models()])
                message = f"> Model `{model_name}` is invalid, available models: {available_models}."

            elif current_bot == BotType.HUGGING_FACE:
                available_models = chatbot.get_available_models()
                message = f"> Model `{model_name}` is invalid, available models: {available_models}."

        logger.info(message)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.exception(f"change_model error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"> Sorry, an error occured while trying to change model.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="reset-model", description="Reset the current model to the default one")
async def reset_model(interaction):
    """
    Command to reset the model to the default one.
    """
    try:
        default_model = None

        if current_bot == BotType.POE:
            default_model = config.POE_MODEL

        elif current_bot == BotType.HUGGING_FACE:
            default_model = config.HUGGING_FACE_MODEL

        success = chatbot.change_model(default_model)
        if success:
            message = f"> Model has been reset to the default one: `{default_model}`."
            logger.info(message)
        else:
            message = f"> Failed to reset the model to the default one: `{default_model}`."
            logger.warning(message)

        await interaction.response.send_message(message)
    except Exception as e:
        logger.exception(f"reset_model error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"> Sorry, an error occured while trying to reset model.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="change-token", description="Change the API token")
async def change_token(interaction, token: str):
    """
    Command to change the API token.
    """
    try:
        success = chatbot.change_token(token)
        if success:
            message = "> API token has been changed."
            logger.info(message)
        else:
            message = "> Failed to change API token."
            logger.warning(message)

        await interaction.response.send_message(message)
    except Exception as e:
        logger.exception(f"change_token error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"> Sorry, an error occured while trying to change token.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="reset-token", description="Reset the API token to the default one")
async def reset_token(interaction):
    """
    Command to reset the API token to the default one.
    """
    try:
        success = chatbot.change_token(config.HUGGING_FACE_TOKEN)
        if success:
            message = "> API token has been reset to the default one."
            logger.info(message)
        else:
            message = "> Failed to reset API token to the default one."
            logger.warning(message)

        await interaction.response.send_message(message)
    except Exception as e:
        logger.exception(f"reset_token error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"> Sorry, an error occured while trying to reset token.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="clear-context", description="Clear context")
async def clear_context(interaction):
    """
    Command to clear the context of the chatbot.
    """
    try:
        chatbot.clear_context()
        message = "> Context has been cleared."
        logger.info(message)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.exception(f"clear_context error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"> Sorry, an error occured while trying to clear context.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="enable-channel-monitoring", description="Enable monitoring of the current channel")
async def enable_channel_monitoring(interaction):
    """
    Command to enable the current channel monitoring.
    """
    global current_channel_monitor_mode

    if current_channel_monitor_mode == ChannelMonitorMode.NONE:
        if interaction.channel_id in channel_whitelist:
            message = "> This channel is already being monitored."
        else:
            channel_whitelist.append(interaction.channel_id)
            message = "> This channel has been added to the monitoring whitelist."

    elif current_channel_monitor_mode == ChannelMonitorMode.ALL:
        if interaction.channel_id in channel_blacklist:
            channel_blacklist.remove(interaction.channel_id)
            message = "> This channel has been removed from the monitoring blacklist."
        else:
            message = "> This channel is already being monitored."

    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="disable-channel-monitoring", description="Disable monitoring of the current channel")
async def disable_channel_monitoring(interaction):
    """
    Command to disable the current channel monitoring.
    """
    global current_channel_monitor_mode

    if current_channel_monitor_mode == ChannelMonitorMode.NONE:
        if interaction.channel_id in channel_whitelist:
            channel_whitelist.remove(interaction.channel_id)
            message = "> This channel has been removed from the monitoring whitelist."
        else:
            message = "> This channel is already not being monitored."

    elif current_channel_monitor_mode == ChannelMonitorMode.ALL:
        if interaction.channel_id in channel_blacklist:
            message = "> This channel is already not being monitored."
        else:
            channel_blacklist.append(interaction.channel_id)
            message = "> This channel has been added to the monitoring blacklist."

    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="get-channel-whitelist", description="Get the channel whitelist")
async def get_channel_whitelist(interaction):
    """
    Command to get the channel whitelist.
    """
    global channel_whitelist

    if len(channel_whitelist) == 0:
        message = "There are no whitelisted channels."
    else:
        channel_list = ", ".join(
            [f"`{client.get_channel(channel)} ({channel})`" for channel in channel_whitelist])
        message = f"> The whitelisted channels are: {channel_list}."

    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="get-channel-blacklist", description="Get the channel blacklist")
async def get_channel_blacklist(interaction):
    """
    Command to get the channel blacklist.
    """
    global channel_blacklist

    if len(channel_blacklist) == 0:
        message = "There are no blacklisted channels"
    else:
        channel_list = ", ".join(
            [f"`{client.get_channel(channel)} ({channel})`" for channel in channel_blacklist])
        message = f"> The blacklisted channels are: {channel_list}."

    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="get-channel-monitor-mode", description="Get the current monitoring mode")
async def get_channel_monitor_mode(interaction):
    """
    Command to get the current channel monitoring mode.
    """
    global current_channel_monitor_mode

    message = f"> The current monitoring mode is `{current_channel_monitor_mode.value}`."
    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="change-channel-monitor-mode", description="Change the current monitoring mode")
async def change_channel_monitor_mode(interaction, new_mode: str):
    """
    Command to change the current channel monitoring mode.
    """
    success = change_channel_monitor_mode(new_mode)

    if success:
        message = f"> The monitoring mode has been changed to `{current_channel_monitor_mode.value}`."
    else:
        modes = ", ".join([f"`{mode.value}`" for mode in ChannelMonitorMode])
        message = f"> Invalid mode. Available modes are: {modes}."

    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="enable-name-prefix", description="Enable prefixing username / nickname to chat messages")
async def enable_name_prefix(interaction):
    """
    Command to enable name prefix.
    """
    change_name_prefix_mode(True)
    message = f"> Enabled name prefix"
    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="disable-name-prefix", description="Disable prefixing username / nickname to chat messages")
async def disable_name_prefix(interaction):
    """
    Command to disable name prefix.
    """
    change_name_prefix_mode(False)
    message = f"> Disabled name prefix"
    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="register-nickname", description="Register / update a nickname")
async def register_nickname(interaction, nickname: str):
    """
    Registers or updates a nickname for the user who sent the command.
    """
    author_name = interaction.user.name

    # Check if nickname already exists
    if author_name in nicknames:
        message = f"> Your nickname has been updated to `{nickname}`."
    else:
        message = f"> Your nickname `{nickname}` has been registered."

    # Update the nickname
    nicknames[author_name] = nickname

    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="unregister-nickname", description="Unregister a nickname if registered")
async def unregister_nickname(interaction):
    """
    Unregisters the nickname for the user who sent the command.
    """
    author_name = interaction.user.name

    # Check if nickname exists
    if author_name in nicknames:
        del nicknames[author_name]
        message = f"> Your nickname has been unregistered."
    else:
        message = f"> You don't have a registered nickname."

    logger.info(message)
    await interaction.response.send_message(content=message)


@tree.command(name="get-nickname", description="Get the nickname if registered")
async def get_nickname(interaction):
    """
    Returns the nickname for the user who sent the command.
    """
    author_name = interaction.user.name

    # Check if nickname exists
    if author_name in nicknames:
        message = f"> Your current nickname is `{nicknames[author_name]}`."
    else:
        message = f"> You don't have a registered nickname."

    logger.info(message)
    await interaction.response.send_message(content=message)


@client.event
async def on_ready():
    """
    Event that runs when the Discord client is ready.
    """
    logger.info(f'Logged in as {client.user}')

    # Register the command tree for Discord slash commands
    await tree.sync()


@client.event
async def on_message(message):
    """
    Event that runs when a message is sent in a Discord server that the client is connected to.

    If the message is not sent by the bot itself, get a response from the chatbot and send it to the same channel.
    """
    try:
        # Ignore messages sent by the bot itself
        if message.author == client.user:
            return

        # Check if current mode is NONE, and only query messages in the whitelist
        if current_channel_monitor_mode == ChannelMonitorMode.NONE:
            if message.channel.id not in channel_whitelist:
                return

        # Check if current mode is ALL, and ignore messages in the blacklist
        elif current_channel_monitor_mode == ChannelMonitorMode.ALL:
            if message.channel.id in channel_blacklist:
                return

        user_input = message.content

        # Ignore messages that start with '$ignore'
        if user_input.startswith('$ignore'):
            return

        # Add name prefix
        if current_name_prefix_mode:
            author_name = nicknames.get(
                message.author.name, message.author.name)
            user_input = add_prefix_to_message(f"{author_name}: ", user_input)

        # Get response from chatbot
        logger.info(f"Input from {message.author}: {user_input}")

        async with message.channel.typing():
            status, response = await query(user_input)

            response = format_response_based_on_status(response, status)

            await message.channel.send(content=response)

    except Exception as e:
        logger.exception(f"on_message error:  {type(e).__name__} - {e}")
        await message.channel.send(content=f"> Sorry, fail to process your request.\n\n`{type(e).__name__} - {e}`")


def get_bot():
    if isinstance(chatbot, PoeChatBot):
        return BotType.POE.value.lower()

    elif isinstance(chatbot, HuggingFaceChatBot):
        return BotType.HUGGING_FACE.value.lower()
    else:
        return None


def change_bot(new_bot):
    """
    Set the chatbot to the given bot_type if the bot_type is valid
    """
    global chatbot, current_bot

    if isinstance(new_bot, str):
        try:
            new_bot = BotType(new_bot.lower())
        except ValueError:
            logger.warning(f"Invalid bot type: {new_bot}")
            return False

    if not isinstance(new_bot, BotType):
        logger.warning(f"Invalid bot type: {type(new_bot)}")
        return False

    if new_bot == BotType.POE:
        chatbot = PoeChatBot(
            config.POE_TOKEN, config.POE_MODEL, config.POE_PROXY)

    elif new_bot == BotType.HUGGING_FACE:
        chatbot = HuggingFaceChatBot(
            config.HUGGING_FACE_TOKEN, config.HUGGING_FACE_MODEL)

    current_bot = new_bot
    return True


def change_channel_monitor_mode(new_mode):
    global current_channel_monitor_mode

    if isinstance(new_mode, str):
        try:
            new_mode = ChannelMonitorMode(new_mode.lower())
        except ValueError:
            logger.warning(f"Invalid channel monitor mode: {new_mode}")
            return False

    if not isinstance(new_mode, ChannelMonitorMode):
        logger.warning(f"Invalid channel monitor mode type: {type(new_mode)}")
        return False

    current_channel_monitor_mode = new_mode
    return True


def change_name_prefix_mode(new_mode):
    global current_name_prefix_mode
    current_name_prefix_mode = new_mode


async def query(message: str):
    status = None

    try:
        success, response = await chatbot.query(message, debug=config.DEBUG)
    except AttributeError as e:
        status = QueryStatus.QUERY_ATTRIBUTE_ERROR
        logger.error(
            f"Query AttributeError:  {type(e).__name__} - {e}, trying to re-initialize the chatbot")
        change_bot(current_bot)
        return status, e
    except Exception as e:
        status = QueryStatus.UNKNOWN_QUERY_ERROR
        logger.exception(f"Query error:  {type(e).__name__} - {e}")
        return status, e

    # Empty response
    if len(response) == 0:
        status = QueryStatus.EMPTY_RESPONSE_ERROR
        logger.error(f"Empty response")
        return status, "Empty response"

    # Send response to the same channel
    if success:
        status = QueryStatus.SUCCESS
        logger.info(f"Response: {response}")
        return status, response
    else:
        status = QueryStatus.UNKNOWN_RESPONSE_ERROR

        logger.error(f"Response error: {response}")
        error_message = f"{response}"
        return status, error_message


def add_prefix_to_message(prefix: str, message: str):
    return f"{prefix}{message}"


def format_response_based_on_status(response: str, status: QueryStatus):
    if status == QueryStatus.SUCCESS:
        return response

    elif status == QueryStatus.QUERY_ATTRIBUTE_ERROR:
        return f"> Sorry, your request couldn't be sent, trying to re-initialize the chatbot, please retry few seconds later, below are the response received:\n\n{response}"

    elif status == QueryStatus.UNKNOWN_QUERY_ERROR:
        return f"> Sorry, your request couldn't be sent, below are the response received:\n\n{response}"

    elif status == QueryStatus.EMPTY_RESPONSE_ERROR:
        return f"> Sorry, something wrong with the response, below are the response received:\n\n{response}"

    elif status == QueryStatus.UNKNOWN_RESPONSE_ERROR:
        return f"> Sorry, your request couldn't be processed, below are the response received:\n\n{response}"


def main():
    global chatbot, current_monitor_mode, current_name_prefix_mode

    parser = argparse.ArgumentParser()
    parser.add_argument('--bot', type=str, choices=[bot.value for bot in BotType],
                        default=BotType.POE.value, help='Select the chatbot to use')
    parser.add_argument('--model', type=str, default=None,
                        help='Select the chatbot model to use')
    parser.add_argument('--channel-monitor-mode', type=str, choices=[
                        mode.value for mode in ChannelMonitorMode], default=ChannelMonitorMode.ALL.value, help='Select the channel monitor mode')
    parser.add_argument('--enable-name-prefix', type=bool, choices=[
                        True, False], default=True, help='Enable or disable prefixing user names to chat messages. Default is True.')

    args = parser.parse_args()

    # Set default bot
    change_bot(args.bot)

    # Set default model
    if args.model:
        chatbot.change_model(args.model)

    # Set default channel monitor mode
    change_channel_monitor_mode(args.channel_monitor_mode)

    # Set default enable name prefix
    change_name_prefix_mode(args.enable_name_prefix)

    client.run(config.DISCORD_TOKEN, log_handler=None)


if __name__ == '__main__':
    main()
