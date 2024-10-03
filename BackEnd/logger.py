import logging
import os

class Logger():
    def __init__ (self, logFile):
        # if os.path.exists(logFile):
        #     os.remove(logFile)

        logger = logging.getLogger(__name__)

        if not logger.hasHandlers():
            fileHandler = logging.FileHandler(logFile,encoding='utf-8')
            logFormat = logging.Formatter('%(levelname)s - %(asctime)s ::: %(message)s')
            fileHandler.setFormatter(logFormat)

            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            logger.addHandler(fileHandler)

        self.logger = logger

def TGLogger():
    return Logger('tg.log').logger
def ParserLogger():
    return Logger('parser.log').logger