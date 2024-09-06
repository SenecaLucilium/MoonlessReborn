import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler
)

from selenium.webdriver.firefox.webdriver import WebDriver

class BotAPI ():
    def __init__(self, driver: WebDriver):
        with open('data.json', 'r') as file:
                token = json.load(file)['token']
        self.application = ApplicationBuilder().token(token).build()