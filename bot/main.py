import logging

from config import settings
from bot.bot import Bot
from bot.log_handler import add_handler
from bot.commands import register_commands



def create_bot():
    add_handler()
    bot = Bot(settings.BOT_TOKEN)
    register_commands(bot)
    return bot

# Creating the bot instance here
# Use for run and for send messages when the condition is satisfied.
bot = create_bot()