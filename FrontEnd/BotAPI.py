import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from BackEnd.logger import TGLogger
from BackEnd.articleObject import Article

LOGGER = TGLogger()

class BotAPI():
    def __init__ (self):
        LOGGER.info ('BotAPI init.')

        with open('Data/articles.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.articles = { Article(
                article["name"],
                article["authorName"],
                article["authorLink"],
                article["URL"],
                article["creationDate"],
                article["telegraphLinks"],
                article["tags"]
            )
            for article in data
        }
        LOGGER.info (f'Downloaded {len(self.articles)} articles.')

        with open('Data/data.json', 'r', encoding='utf-8') as file:
            token = json.load(file)['token']
        
        self.application = ApplicationBuilder().token(token).build()

        startHandler = CommandHandler ('start', self.start)
        helpHandler = CommandHandler ('help', self.help)
        getHandler = CommandHandler ('get', self.get)
        findNameHandler = CommandHandler ('find_name', self.findName)
        fullHandler = CommandHandler ('full', self.full)
        reportHandler = CommandHandler ('report', self.report)  
        credentialsHandler = CommandHandler ('credentials', self.credentials)
        unknownHandler = MessageHandler (filters.COMMAND, self.unknown)

        self.application.add_handler (startHandler)
        self.application.add_handler (helpHandler)
        self.application.add_handler (getHandler)
        self.application.add_handler (findNameHandler)
        self.application.add_handler (fullHandler)
        self.application.add_handler (reportHandler)
        self.application.add_handler (credentialsHandler)
        self.application.add_handler (unknownHandler)

        LOGGER.info('BotAPI initialized, run polling.')
        self.application.run_polling (allowed_updates=Update.ALL_TYPES)
    
    @staticmethod
    async def unknown (update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            LOGGER.info(f"Got unknown message from user_id: {context._user_id}")
            msg = (
                "Неизвестная команда.\n"
                "Вызовите /help чтобы увидеть список доступных команд."
            )
            await context.bot.sendMessage (
                chat_id=update.effective_chat.id,
                text=msg
            )
        except Exception as error:
            LOGGER.error(f'Something went wrong at unknown handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")
    
    @staticmethod
    async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            LOGGER.info(f"Got start message from user_id: {context._user_id}, with args: {''.join(context.args)}")
            msg = (
                "Этот бот находится в стадии разработки. Помните, что вы не можете запрашивать статьи, которым меньше месяца.\n"
                "\n"
                "Бот возвращает статьи в телеграфах (telegra.ph).\n"
                "\n"
                "⚙️<b>Основные команды:</b>\n"
                "/start - запуск бота\n"
                "/get [url] - получить статью по ссылке с бусти\n"
                "/find_name [name] - получить статью по имени (УКАЗЫВАЙТЕ ЧЁТКОЕ ИМЯ)\n"
                "/help - помощь и полный список команд\n"
            )
            await context.bot.sendMessage (
                chat_id=update.effective_chat.id,
                text=msg,
                parse_mode='html'
            )
        except Exception as error:
            LOGGER.error(f'Something went wrong at start handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")
    
    @staticmethod
    async def help (update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            LOGGER.info(f"Got help message from user_id: {context._user_id}, with args: {''.join(context.args)}")
            msg = (
                "<b>Полный список команд:</b>\n"
                "\n"
                "⚙️<b>Меню:</b>\n"
                "/start - запуск бота\n"
                "/help - помощь и полный список команд\n"
                "\n"
                "📚<b>Статьи</b>\n"
                "/get [url] - получить статью по ссылке с бусти\n"
                "/find_name [name] - получить статью по имени\n"
                "/full - получить полный дамп статей\n"
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
            LOGGER.error(f'Something went wrong at help handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")
    
    async def get (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            LOGGER.info(f"Got get message from user_id: {context._user_id}, with args: {''.join(context.args)}")
            waitingMessage = await update.effective_message.reply_text("Подождите...")
            
            if len (context.args) != 1:
                raise ValueError
            
            userURL = context.args[0]
            if '?share=post_link' in userURL:
                userURL = userURL[:-1 * len('?share=post_link')]

            for article in self.articles:
                if userURL == article.URL:
                    await waitingMessage.edit_text ('\n'.join(article.telegraphLinks))
                    userURL = None
            if userURL is not None:
                await waitingMessage.edit_text ('Такой статьи не найдено...')
        except ValueError as error:
            LOGGER.error(f'Got ValueError at get handler with error: {error}')
            await waitingMessage.edit_text ("Корректное использование: /get [url].")
        except Exception as error:
            LOGGER.error(f'Something went wrong at get handler with error: {error}')
            await waitingMessage.edit_text ("Произошла неизвестная ошибка.")
    
    async def findName (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            LOGGER.info(f"Got find_name message from user_id: {context._user_id}, with args: {''.join(context.args)}")
            waitingMessage = await update.effective_message.reply_text("Подождите...")
            
            userName = ' '.join(context.args)
            for article in self.articles:
                if userName == article.name:
                    await waitingMessage.edit_text ('\n'.join(article.telegraphLinks))
                    userName = None
            if userName is not None:
                await waitingMessage.edit_text ('Такой статьи не найдено...')
        except Exception as error:
            LOGGER.error(f'Something went wrong at find_name handler with error: {error}')
            await waitingMessage.edit_text ("Произошла неизвестная ошибка.")
    
    async def full (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            LOGGER.info(f"Got full message from user_id: {context._user_id}")
            waitingMessage = await update.effective_message.reply_text("Подождите...")

            articlesJSON = open('Data/articles.json', 'rb')
            await update.effective_message.reply_document(articlesJSON)
        except Exception as error:
            LOGGER.error(f'Something went wrong at full handler with error: {error}')
            await waitingMessage.edit_text ("Произошла неизвестная ошибка.")

    async def report (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            LOGGER.info(f"Got report message from user_id: {context._user_id}, with args: {''.join(context.args)}")
            if len (context.args) < 0:
                raise ValueError
            with open('Data/data.json', 'r', encoding='utf-8') as file:
                admin_id = json.load(file)['admin_id']
            
            reportMessage = " ".join (context.args)

            await context.bot.sendMessage (
                chat_id=admin_id,
                text=f"Вам пришел репорт от юзера:\n{reportMessage}"
            )
            LOGGER.info('Sent report to the Admin.')

            await context.bot.sendMessage (
                chat_id=update.effective_chat.id,
                text="Репорт отправлен."
            )
        except ValueError as error:
            LOGGER.error(f'Got ValueError at report handler with error: {error}')
            await update.effective_message.reply_text ("Корректное использование: /report [message].")
        except Exception as error:
            LOGGER.error(f'Something went wrong at report handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")
    
    async def credentials (self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            LOGGER.info(f"Got credentials message from user_id: {context._user_id}")
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
            LOGGER.error(f'Somethin went wrong at credentials handler with error: {error}')
            await update.effective_message.reply_text ("Произошла неизвестная ошибка.")