import logging
import os

class Logger():
    def __init__ (self, logFile='app.log'):
        # if os.path.exists(logFile):
        #     os.remove(logFile)

        logger = logging.getLogger(__name__)

        if not logger.hasHandlers():
            fileHandler = logging.FileHandler(logFile)
            logFormat = logging.Formatter('%(levelname)s - %(asctime)s ::: %(message)s')
            fileHandler.setFormatter(logFormat)

            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            logger.addHandler(fileHandler)

        self.logger = logger