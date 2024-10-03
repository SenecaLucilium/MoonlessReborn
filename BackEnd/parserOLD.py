from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from telegraph import Telegraph
from datetime import datetime, timedelta

from BackEnd.logger import Logger
logger = Logger()


def checkDate (html: str) -> bool | None:
    try:
        logger.logger.info (f'Checking date for an article...')
        date_element = BeautifulSoup(html, 'html.parser').find('span', class_='CreatedAt_headerLink_CEfWB')

        date_str = date_element.text.strip()
        date_obj = None

        try:
            date_obj = datetime.strptime(date_str, "%b %d %H:%M")
            date_obj = date_obj.replace(year=datetime.now().year)
        except ValueError:
            date_obj = datetime.strptime(date_str, "%b %d %Y %H:%M")
        
        if datetime.now() - date_obj > timedelta(days=30):
            logger.logger.info ('Correct time.')
            return True
        else:
            logger.logger.warning ('Incorrect time.')
            return False
    except Exception as error:
        logger.logger.info (f'Something went wrong, while checking date with an errror: {error}')
        return None