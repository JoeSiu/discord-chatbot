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


# Initialize channel whitelist and blacklist
channel_whitelist = []
channel_blacklist = []

# Current bot
current_bot = BotType.POE

# Current monitor mode
current_channel_monitor_mode = ChannelMonitorMode.ALL


@tree.command(name="get-bot", description="Get the current chatbot")
async def get_bot(interaction):
    """
    Command to get the current chatbot.
    """
    try:
        bot_name = get_bot()
        message = f"The current chatbot is: `{bot_name}`"
        logger.info(message)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.info("get_bot error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"Sorry, an error occured while trying to get bot.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="change-bot", description="Change the current bot")
async def change_bot(interaction, bot_name: str):
    """
    Command to change the current chatbot.
    """
    try:

        # Defer sending message as changing bot takes time
        await interaction.response.defer()

        success = change_bot_str(bot_name)

        if success:
            message = f"Bot has been changed to: `{bot_name}`"
            logger.info(message)
            await interaction.followup.send(message)
        else:
            bots = ", ".join([bot.value for bot in BotType])
            message = f"Bot `{bot_name}` is invalid, available bot: {bots}"
            logger.info(message)
            await interaction.followup.send(message)
    except Exception as e:
        logger.info("change_bot error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"Sorry, an error occured while trying to change bot.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="get-model", description="Get the current chatbot model")
async def get_model(interaction):
    """
    Command to get the current chatbot model.
    """
    try:
        model_name = chatbot.get_model()
        message = f"The current chatbot model is: `{model_name}`"
        logger.info(message)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.info("get_model error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"Sorry, an error occured while trying to get model.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="change-model", description="Change the chatbot model")
async def change_model(interaction, model_name: str):
    """
    Command to change the chatbot model.
    """
    try:
        success = chatbot.change_model(model_name)
        if success:
            message = f"Model has been changed to: `{model_name}`"
            logger.info(message)
            await interaction.response.send_message(message)
        else:
            if isinstance(chatbot, PoeChatBot):
                available_models = ", ".join(
                    [f"`{value}`" for key, value in chatbot.get_available_models()])
                message = f"Model `{model_name}` is invalid, available models: {available_models}"
            elif isinstance(chatbot, HuggingFaceChatBot):
                message = f"Model `{model_name}` is invalid, please visit https://huggingface.co/models?pipeline_tag=conversational to get a list of available models."
            logger.warning(message)
            await interaction.response.send_message(message)
    except Exception as e:
        logger.info("change_model error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"Sorry, an error occured while trying to change model.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="reset-model", description="Reset the current Hugging Face model to the default one")
async def reset_model(interaction):
    """
    Command to reset the Hugging Face model to the default one.
    """
    try:
        success = chatbot.change_model(config.HUGGING_FACE_MODEL)
        if success:
            message = f"Model has been reset to the default one: `{config.HUGGING_FACE_MODEL}`"
            logger.info(message)
            await interaction.response.send_message(message)
        else:
            message = f"Failed to reset the model to the default one: `{config.HUGGING_FACE_MODEL}`"
            logger.error(message)
            await interaction.response.send_message(message)
    except Exception as e:
        logger.info("reset_model error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"Sorry, an error occured while trying to reset model.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="change-token", description="Change Hugging Face API token")
async def change_token(interaction, token: str):
    """
    Command to change the Hugging Face API token.
    """
    try:
        success = chatbot.change_token(token)
        if success:
            message = "API token has been changed"
            logger.info(message)
            await interaction.response.send_message(message)
        else:
            message = "Failed to change API token"
            logger.error(message)
            await interaction.response.send_message(message)
    except Exception as e:
        logger.info("change_token error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"Sorry, an error occured while trying to change token.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="reset-token", description="Reset the Hugging Face API token to the default one")
async def reset_token(interaction):
    """
    Command to reset the Hugging Face API token to the default one.
    """
    try:
        success = chatbot.change_token(config.HUGGING_FACE_TOKEN)
        if success:
            message = "API token has been reset to the default one"
            logger.info(message)
            await interaction.response.send_message(message)
        else:
            message = "Failed to reset API token to the default one"
            logger.error(message)
            await interaction.response.send_message(message)
    except Exception as e:
        logger.info("reset_token error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"Sorry, an error occured while trying to reset token.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="clear-context", description="Clear context")
async def clear_context(interaction):
    """
    Command to clear the context of the chatbot.
    """
    try:
        chatbot.clear_context()
        message = "Context has been cleared"
        logger.info(message)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.info("clear_context error:  {type(e).__name__} - {e}")
        await interaction.response.send_message(f"Sorry, an error occured while trying to clear context.\n\n`{type(e).__name__} - {e}`")


@tree.command(name="enable-channel-monitoring", description="Enable monitoring of the current channel")
async def enable_channel_monitoring(interaction):
    """
    Command to enable the current channel monitoring.
    """
    global current_channel_monitor_mode

    if current_channel_monitor_mode == ChannelMonitorMode.NONE:
        if interaction.channel_id in channel_whitelist:
            await interaction.response.send_message(content="This channel is already being monitored.")
        else:
            channel_whitelist.append(interaction.channel_id)
            await interaction.response.send_message(content="This channel has been added to the monitoring whitelist.")

    elif current_channel_monitor_mode == ChannelMonitorMode.ALL:
        if interaction.channel_id in channel_blacklist:
            channel_blacklist.remove(interaction.channel_id)
            await interaction.response.send_message(content="This channel has been removed from the monitoring blacklist.")
        else:
            await interaction.response.send_message(content="This channel is already being monitored.")


@tree.command(name="disable-channel-monitoring", description="Disable monitoring of the current channel")
async def disable_channel_monitoring(interaction):
    """
    Command to disable the current channel monitoring.
    """
    global current_channel_monitor_mode

    if current_channel_monitor_mode == ChannelMonitorMode.NONE:
        if interaction.channel_id in channel_whitelist:
            channel_whitelist.remove(interaction.channel_id)
            await interaction.response.send_message(content="This channel has been removed from the monitoring whitelist.")
        else:
            await interaction.response.send_message(content="This channel is already not being monitored.")

    elif current_channel_monitor_mode == ChannelMonitorMode.ALL:
        if interaction.channel_id in channel_blacklist:
            await interaction.response.send_message(content="This channel is already not being monitored.")
        else:
            channel_blacklist.append(interaction.channel_id)
            await interaction.response.send_message(content="This channel has been added to the monitoring blacklist.")


@tree.command(name="get-channel-whitelist", description="Get the channel whitelist")
async def get_channel_whitelist(interaction):
    """
    Command to get the channel whitelist.
    """
    global channel_whitelist

    if len(channel_whitelist) == 0:
        await interaction.response.send_message(content="There are no whitelisted channels.")
    else:
        channel_list = ", ".join(
            [f"`{channel.name} ({channel.id})`" for channel in channel_whitelist])
        await interaction.response.send_message(content=f"The whitelisted channels are: {channel_list}.")


@tree.command(name="get-channel-blacklist", description="Get the channel blacklist")
async def get_channel_blacklist(interaction):
    """
    Command to get the channel blacklist.
    """
    global channel_blacklist

    if len(channel_blacklist) == 0:
        await interaction.response.send_message(content="There are no blacklisted channels.")
    else:
        channel_list = ", ".join(
            [f"`{channel.name} ({channel.id})`" for channel in channel_blacklist])
        await interaction.response.send_message(content=f"The blacklisted channels are: {channel_list}.")


@tree.command(name="get-channel-monitor-mode", description="Get the current monitoring mode")
async def get_channel_monitor_mode(interaction):
    """
    Command to get the current channel monitoring mode.
    """
    global current_channel_monitor_mode
    await interaction.response.send_message(content=f"The current monitoring mode is `{current_channel_monitor_mode.value}`.")


@tree.command(name="change-channel-monitor-mode", description="Change the current monitoring mode")
async def change_channel_monitor_mode(interaction, new_mode: str):
    """
    Command to change the current channel monitoring mode.
    """
    global current_channel_monitor_mode
    if new_mode.lower() not in [mode.value.lower() for mode in ChannelMonitorMode]:
        modes = ", ".join([f"`{mode.value}`" for mode in ChannelMonitorMode])
        await interaction.response.send_message(content=f"Invalid mode. Available modes are: {modes}")
        return

    current_channel_monitor_mode = ChannelMonitorMode[new_mode.upper()]
    await interaction.response.send_message(content=f"The monitoring mode has been changed to `{current_channel_monitor_mode.value}`.")


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

        # Get response from chatbot
        logger.info(f"Input: {user_input}")

        async with message.channel.typing():
            try:
                success, response = await chatbot.query(user_input, debug=config.DEBUG)
            except AttributeError as e:
                logger.error(
                    f"Query error:  {type(e).__name__} - {e}, trying to re-initialize the chatbot")
                await message.channel.send(content=f"Sorry, your request couldn't be sent, trying to re-initialize the chatbot, please retry few seconds later.\n\n`{type(e).__name__} - {e}`")
                change_bot(current_bot)
                return
            except Exception as e:
                logger.error(f"Query error:  {type(e).__name__} - {e}")
                await message.channel.send(content=f"Sorry, your request couldn't be sent.\n\n`{type(e).__name__} - {e}`")
                return

        # Empty response
        if len(response) == 0:
            logger.error(f"Response is empty!")
            await message.channel.send(content=f"Sorry, something wrong with the response.\n\n`Response is empty`")
            return

        # Send response to the same channel
        if success:
            logger.info(f"Response: {response}")
            await message.channel.send(content=str(response))
        else:
            logger.error(f"Response error: {response}")
            error_message = f"Sorry, your request couldn't be processed.\n\n`{str(response)}`"
            await message.channel.send(content=error_message)

    except Exception as e:
        logger.error(f"on_message error:  {type(e).__name__} - {e}")
        await message.channel.send(content=f"Sorry, fail to process your request.\n\n`{type(e).__name__} - {e}`")


def get_bot():
    if isinstance(chatbot, PoeChatBot):
        return BotType.POE.value.lower()

    elif isinstance(chatbot, HuggingFaceChatBot):
        return BotType.HUGGING_FACE.value.lower()
    else:
        return None


def change_bot(bot_type: BotType):
    """
    Set the chatbot to the given bot_type if the bot_type is valid
    """
    global chatbot, current_bot

    if bot_type not in BotType:
        return False

    if bot_type == BotType.POE:
        chatbot = PoeChatBot(
            config.POE_TOKEN, config.POE_MODEL, config.POE_PROXY)

    elif bot_type == BotType.HUGGING_FACE:
        chatbot = HuggingFaceChatBot(
            config.HUGGING_FACE_TOKEN, config.HUGGING_FACE_MODEL)

    current_bot = bot_type
    return True


def change_bot_str(bot_name: str):
    """
    Convert bot_name string to BotType enum and call change_bot function.
    """
    try:
        bot_type = BotType(bot_name.lower())
    except ValueError:
        return False
    return change_bot(bot_type)


def main():
    global chatbot

    parser = argparse.ArgumentParser()
    parser.add_argument('--bot', type=str, choices=[
                        'poe', 'hugging-face'], default='poe', help='Select the chatbot to use')
    args = parser.parse_args()

    change_bot_str(args.bot)

    client.run(config.DISCORD_TOKEN, log_handler=None)


if __name__ == '__main__':
    main()
