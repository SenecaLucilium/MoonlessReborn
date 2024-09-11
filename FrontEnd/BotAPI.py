import json

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from selenium.webdriver.firefox.webdriver import WebDriver
from BackEnd.parser import getArticleByUrl

from BackEnd.logger import Logger
logger = Logger()

class BotAPI ():
    def __init__(self, driver: WebDriver):
        logger.logger.info('BotAPI init.')

        self.driver = driver
        with open('data.json', 'r') as file:
                token = json.load(file)['token']
        self.application = ApplicationBuilder().token(token).build()

        startHandler = CommandHandler ('start', self.start)
        helpHandler = CommandHandler ('help', self.help)
        getHandler = CommandHandler ('get', self.get)
        reportHandler = CommandHandler ('report', self.report)
        credentialsHandler = CommandHandler ('credentials', self.credentials)
        unknownHandler = MessageHandler (filters.COMMAND, self.unknown)

        self.application.add_handler (startHandler)
        self.application.add_handler (helpHandler)
        self.application.add_handler (getHandler)
        self.application.add_handler (reportHandler)
        self.application.add_handler (credentialsHandler)
        self.application.add_handler (unknownHandler)

        logger.logger.info('BotAPI initialized, run polling.')
        self.application.run_polling (allowed_updates=Update.ALL_TYPES)
    
    @staticmethod
    async def unknown (update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            logger.logger.info(f"Got unknown message from user_id: {context._user_id}, with args: {''.join(context.args)}")
            msg = (
                "Неизвестная команда.\n"
                "Вызовите /help чтобы увидеть список доступных команд."
            )
            await context.bot.sendMessage (
                chat_id=update.effective_chat.id,
                text=msg
            )
        except Exception as error:
            logger.logger.error(f'Something went wrong at unknown handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")
    
    @staticmethod
    async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            logger.logger.info(f"Got start message from user_id: {context._user_id}, with args: {''.join(context.args)}")
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
        except Exception as error:
            logger.logger.error(f'Something went wrong at start handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")
    
    @staticmethod
    async def help (update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            logger.logger.info(f"Got help message from user_id: {context._user_id}, with args: {''.join(context.args)}")
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
        except Exception as error:
            logger.logger.error(f'Something went wrong at help handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")
    
    async def get (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            logger.logger.info(f"Got get message from user_id: {context._user_id}, with args: {''.join(context.args)}")
            waitingMessage = await update.effective_message.reply_text("Подождите...")
            
            if len (context.args) != 1:
                raise ValueError
            
            telegraph_urls = getArticleByUrl (self.driver, context.args[0])
            if telegraph_urls is None:
                logger.logger.warning('Telegraph_urls is None, sending Error message.')
                await waitingMessage.edit_text ("Произошла ошибка во время получения статьи.")
            else:
                logger.logger.info('Telegraph_urls is not None, sending links.')
                await waitingMessage.edit_text ('\n'.join(telegraph_urls))
        except ValueError as error:
            logger.logger.error(f'Got ValueError at get handler with error: {error}')
            await waitingMessage.edit_text ("Корректное использование: /get [url].")
        except PermissionError as error:
            logger.logger.error(f'Got PermissionError at get handler with error: {error}')
            await waitingMessage.edit_text ("Нельзя запрашивать статьи, которым меньше месяца.")
        except Exception as error:
            logger.logger.error(f'Something went wrong at get handler with error: {error}')
            await waitingMessage.edit_text ("Произошла неизвестная ошибка.")
    
    async def report (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            logger.logger.info(f"Got report message from user_id: {context._user_id}, with args: {''.join(context.args)}")
            if len (context.args) < 0:
                raise ValueError
            with open('data.json', 'r') as file:
                admin_id = json.load(file)['admin_id']
            
            reportMessage = " ".join (context.args)

            await context.bot.sendMessage (
                chat_id=admin_id,
                text=f"Вам пришел репорт от юзера:\n{reportMessage}"
            )
            logger.logger.info('Sent report to the Admin.')

            await context.bot.sendMessage (
                chat_id=update.effective_chat.id,
                text="Репорт отправлен."
            )
        except ValueError as error:
            logger.logger.error(f'Got ValueError at report handler with error: {error}')
            await update.effective_message.reply_text ("Корректное использование: /report [message].")
        except Exception as error:
            logger.logger.error(f'Something went wrong at report handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")
    
    async def credentials (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            logger.logger.info(f"Got credentials message from user_id: {context._user_id}, with args: {''.join(context.args)}")
            msg=(
                "<b>Статьи принадлежат тем, кому они принадлежат.</b>\n"
                "\n"
                "Создатель Безлуния - <s>@SenecaMoon</s> <b>ЛИКВИДИРОВАН</b>\n"
                "Github бота - https://github.com/SenecaLucilium/MoonlessReborn\n"
                "Подписывайтесь на канал - https://t.me/moonlessLib"
            )

            await context.bot.sendMessage (
                chat_id=update.effective_chat.id,
                text=msg,
                parse_mode='html'
            )
        except Exception as error:
            logger.logger.error(f'Somethin went wrong at credentials handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")