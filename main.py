import discord
from discord import app_commands
import config
from chatbot import ChatBot
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Discord client with appropriate intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Create Hugging Face chatbot object
chatbot = ChatBot(config.HUGGING_FACE_MODEL, config.HUGGING_FACE_API_TOKEN)

# Create command tree for Discord slash commands
tree = app_commands.CommandTree(client)

# Define command tree functions


@tree.command(name="get-model", description="Get the current Hugging Face model")
async def get_model(interaction):
    """
    Command to get the current Hugging Face model.
    """
    model = chatbot.get_model()
    message = f"The current Hugging Face model is: `{model}`"
    logger.info(message)
    await interaction.response.send_message(message)


@tree.command(name="change-model", description="Change Hugging Face model")
async def change_model(interaction, model_name: str):
    """
    Command to change the Hugging Face model.
    """
    success = chatbot.change_model(model_name)
    if success:
        message = f"Model has been changed to: `{model_name}`"
        logger.info(message)
        await interaction.response.send_message(message)
    else:
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
    success = chatbot.change_token(config.HUGGING_FACE_API_TOKEN)
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
                success, bot_response = await chatbot.query(user_input, debug=config.DEBUG)
            except Exception as e:
                logger.error(f"Error: {e}")
                await message.channel.send(content="Sorry, an error occurred while processing your request.\n`{e}`")
                return

        # Send response to the same channel
        if success:
            logger.info(f"Response: {bot_response}")
            await message.channel.send(content=str(bot_response))
        else:
            logger.error(f"Error response: {bot_response}")
            error_message = f"Sorry, your request couldn't be processed.\n`{str(bot_response)}`"
            await message.channel.send(content=error_message)
    except Exception as e:
         logger.error(f"on_message Error: {e}")
         await message.channel.send(content=f"Sorry, fail to process your request.\n`{e}`")

def main():
    client.run(config.DISCORD_TOKEN)


if __name__ == '__main__':
    main()
