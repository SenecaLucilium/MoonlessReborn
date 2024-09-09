import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from selenium.webdriver.firefox.webdriver import WebDriver
from BackEnd.parser import getArticleByUrl

class BotAPI ():
    def __init__(self, driver: WebDriver):
        self.driver = driver
        with open('data.json', 'r') as file:
                token = json.load(file)['token']
        self.application = ApplicationBuilder().token(token).build()

        startHandler = CommandHandler ('start', self.start)
        helpHandler = CommandHandler ('help', self.help)
        getHandler = CommandHandler ('get', self.get)
        unknownHandler = MessageHandler (filters.COMMAND, self.unknown)

        self.application.add_handler (startHandler)
        self.application.add_handler (helpHandler)
        self.application.add_handler (getHandler)
        self.application.add_handler (unknownHandler)

        self.application.run_polling (allowed_updates=Update.ALL_TYPES)
    
    @staticmethod
    async def unknown (update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = (
            "Неизвестная команда.\n"
            "Вызовите /help чтобы увидеть список доступных команд."
        )
        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg
        )
    
    @staticmethod
    async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = (
            "Этот бот находится в стадии разработки. Помните, что вы не можете запрашивать статьи, которым меньше месяца.\n"
            "\n"
            "Бот возвращает статьи в телеграфах (telegra.ph).\n"
            "\n"
            "⚙️<b>Основные команды:</b>\n"
            "/start - запуск бота\n"
            "/get [url] - получить статью по ссылке с бусти\n"
            "/help - помощь и полный список команд\n"
        )
        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode='html'
        )
    
    @staticmethod
    async def help (update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = (
            "<b>Полный список команд:</b>\n"
            "\n"
            "⚙️<b>Меню:</b>\n"
            "/start - запуск бота\n"
            "/help - помощь и полный список команд\n"
            "\n"
            "📚<b>Статьи</b>\n"
            "/get [url] - получить статью по ссылке с бусти\n"
            "\n"
            "📣<b>Дополнительное:</b>\n"
            "/report [message] - сообщить об ошибке\n"
            "/credentials - информация о проекте\n"
        )
        await context.bot.sendMessage (
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode='html'
        )
    
    async def get (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            waitingMessage = await update.effective_message.reply_text("Подождите...")
            
            if len (context.args) != 1:
                raise ValueError
            
            telegraph_urls = getArticleByUrl (self.driver, context.args[0])
            if telegraph_urls is None:
                await waitingMessage.edit_text ("Произошла ошибка во время получения статьи.")
            else:
                await waitingMessage.edit_text ('\n'.join(telegraph_urls))
        except ValueError as error:
            await waitingMessage.edit_text ("Корректное использование: /get [url].")
        except Exception as error:
            await waitingMessage.edit_text ("Произошла неизвестная ошибка.")