from FrontEnd.BotAPI import BotAPI
from boostyLogin import boostyLogin
from BackEnd.logger import Logger
logger = Logger()

logger.logger.info(''.join('-' for _ in range (20)))
logger.logger.info('New Instance')
logger.logger.info(''.join('-' for _ in range (20)))

driver = boostyLogin()
if driver is not None:
    logger.logger.info('Driver is not None, creation TelegramBot API.')
    BotAPI(driver)
else:
    logger.logger.info('Driver is None.')