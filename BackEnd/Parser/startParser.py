import time
import json
from datetime import datetime, timedelta
from .boostyParser import parsePeriod
from .boostyLogin import boostyLogin
from BackEnd.logger import ParserLogger

LOGGER = ParserLogger()

def startParser():
    LOGGER.info(''.join('-' for _ in range (20)))
    LOGGER.info('New Instance')
    LOGGER.info(''.join('-' for _ in range (20)))

    driver = boostyLogin()
    if driver is not None:
        LOGGER.info('Driver is not None, creation TelegramBot API.')
        try:
            while True:
                LOGGER.info('New check.')
                now = datetime.now()
                endTime = (now - timedelta(weeks=4)).replace(hour=23, minute=59, second=59, microsecond=0)
                startTime = endTime - timedelta(weeks=1)
                LOGGER.info(f'Check period: from {startTime} till {endTime}.')

                with open('Data/articles.json', 'r', encoding='utf-8') as file:
                    existingArticles = json.load(file)
                
                parsedArticles = parsePeriod(startTime.strftime("%d.%m.%Y"), endTime.strftime("%d.%m.%Y"), driver)

                if parsedArticles is not None:
                    articlesDict = [article.__dict__ for article in parsedArticles]
                    existingArticles.extend(articlesDict)

                    with open('Data/articles.json', 'w', encoding='utf-8') as file:
                        json.dump(existingArticles, file, ensure_ascii=False, indent=4)

                LOGGER.info('Check ended, now we wait...')
                nextRunTime = datetime.now().replace(hour=23, minute=59, second=59)
                time.sleep(1) # Для избегания отрицательного слипа
                time.sleep((nextRunTime - datetime.now()).total_seconds())

        except Exception as error:
            LOGGER.error(f'Error inside startParser endless cycle with message: {error}.')
    else:
        LOGGER.info('Driver is None.')