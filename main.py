import argparse
import discord
from discord import app_commands
import config
from chatbots.hugging_face_chatbot import HuggingFaceChatBot
from chatbots.poe_chatbot import PoeChatBot
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Discord client with appropriate intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Create chatbot object
chatbot = None

# Create command tree for Discord slash commands
tree = app_commands.CommandTree(client)

# Define command tree functions


@tree.command(name="get-bot", description="Get the current chatbot")
async def get_bot(interaction):
    """
    Command to get the current chatbot.
    """
    bot_name = get_bot()
    message = f"The current chatbot is: `{bot_name}`"
    logger.info(message)
    await interaction.response.send_message(message)


@tree.command(name="change-bot", description="Change the current bot")
async def change_bot(interaction, bot_name: str):
    # Defer sending message as changing bot takes time
    await interaction.response.defer()

    success = change_bot(bot_name)

    if success:
        message = f"Bot has been changed to: `{bot_name}`"
        logger.info(message)
        await interaction.followup.send(message)
    else:
        message = f"Bot `{bot_name}` is invalid, available bot: `poe`, `hugging-face`"
        logger.info(message)
        await interaction.followup.send(message)


@tree.command(name="get-model", description="Get the current chatbot model")
async def get_model(interaction):
    """
    Command to get the current chatbot model.
    """
    model_name = chatbot.get_model()
    message = f"The current chatbot model is: `{model_name}`"
    logger.info(message)
    await interaction.response.send_message(message)


@tree.command(name="change-model", description="Change the chatbot model")
async def change_model(interaction, model_name: str):
    """
    Command to change the chatbot model.
    """
    success = chatbot.change_model(model_name)
    if success:
        message = f"Model has been changed to: `{model_name}`"
        logger.info(message)
        await interaction.response.send_message(message)
    else:
        if isinstance(chatbot, PoeChatBot):
            message = f"Model `{model_name}` is invalid, available models: {chatbot.get_available_models()}"
        elif isinstance(chatbot, HuggingFaceChatBot):
            message = f"Model `{model_name}` is invalid, please visit https://huggingface.co/models?pipeline_tag=conversational to get a list of available models."
        logger.warning(message)
        await interaction.response.send_message(message)


@tree.command(name="reset-model", description="Reset the current Hugging Face model to the default one")
async def reset_model(interaction):
    """
    Command to reset the Hugging Face model to the default one.
    """
    success = chatbot.change_model(config.HUGGING_FACE_MODEL)
    if success:
        message = f"Model has been reset to the default one: `{config.HUGGING_FACE_MODEL}`"
        logger.info(message)
        await interaction.response.send_message(message)
    else:
        message = f"Failed to reset the model to the default one: `{config.HUGGING_FACE_MODEL}`"
        logger.error(message)
        await interaction.response.send_message(message)


@tree.command(name="change-token", description="Change Hugging Face API token")
async def change_token(interaction, token: str):
    """
    Command to change the Hugging Face API token.
    """
    success = chatbot.change_token(token)
    if success:
        message = "API token has been changed"
        logger.info(message)
        await interaction.response.send_message(message)
    else:
        message = "Failed to change API token"
        logger.error(message)
        await interaction.response.send_message(message)


@tree.command(name="reset-token", description="Reset the Hugging Face API token to the default one")
async def reset_token(interaction):
    """
    Command to reset the Hugging Face API token to the default one.
    """
    success = chatbot.change_token(config.HUGGING_FACE_TOKEN)
    if success:
        message = "API token has been reset to the default one"
        logger.info(message)
        await interaction.response.send_message(message)
    else:
        message = "Failed to reset API token to the default one"
        logger.error(message)
        await interaction.response.send_message(message)


@tree.command(name="clear-context", description="Clear context")
async def clear_context(interaction):
    """
    Command to clear the context of the chatbot.
    """
    chatbot.clear_context()
    message = "Context has been cleared"
    logger.info(message)
    await interaction.response.send_message(message)

# Discord client events


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

        # Get response from chatbot
        user_input = message.content
        logger.info(f"Input: {user_input}")

        async with message.channel.typing():
            try:
                success, response = await chatbot.query(user_input, debug=config.DEBUG)
            except Exception as e:
                logger.error(f"Query error: {e}")
                await message.channel.send(content=f"Sorry, your request couldn't be sent.\n`{e}`")
                return

        # Empty response
        if len(response) == 0:
            logger.error(f"Empty response!")
            await message.channel.send(content=f"Sorry, something wrong with the response.")
            return

        # Send response to the same channel
        if success:
            logger.info(f"Response: {response}")
            await message.channel.send(content=str(response))
        else:
            logger.error(f"Response error: {response}")
            error_message = f"Sorry, your request couldn't be processed.\n`{str(response)}`"
            await message.channel.send(content=error_message)

    except Exception as e:
        logger.error(f"on_message Error: {e}")
        await message.channel.send(content=f"Sorry, fail to process your request.\n`{e}`")


def get_bot():
    if isinstance(chatbot, PoeChatBot):
        return 'poe'
    elif isinstance(chatbot, HuggingFaceChatBot):
        return 'hugging-face'
    else:
        return None


def change_bot(bot_name: str):
    global chatbot

    if bot_name == 'poe':
        chatbot = PoeChatBot(
            config.POE_TOKEN, config.POE_MODEL, config.POE_PROXY)
    elif bot_name == 'hugging-face':
        chatbot = HuggingFaceChatBot(
            config.HUGGING_FACE_TOKEN, config.HUGGING_FACE_MODEL)
    else:
        return False

    return True


def main():
    global chatbot

    parser = argparse.ArgumentParser()
    parser.add_argument('--bot', type=str, choices=[
                        'poe', 'huggingface'], default='huggingface', help='Select the chatbot to use')
    args = parser.parse_args()

    change_bot(args.bot)

    client.run(config.DISCORD_TOKEN)


if __name__ == '__main__':
    main()
