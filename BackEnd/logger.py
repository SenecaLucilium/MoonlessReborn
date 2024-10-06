import logging

class Logger():
    def __init__ (self, logFile):
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
    return Logger('Data/tg.log').logger
def ParserLogger():
    return Logger('Data/parser.log').logger