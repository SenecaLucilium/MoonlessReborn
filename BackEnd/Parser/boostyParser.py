from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from .articleParser import getArticleByHtml
from BackEnd.articleObject import Article
from BackEnd.logger import ParserLogger

LOGGER = ParserLogger()
DRIVER = None
URL_TEMPLATE = "https://boosty.to/bazil.topol?isOnlyAllowedPosts=true&postsFrom={}&postsTo={}"

def getWeekRanges(startDate: datetime, endDate: datetime) -> list:
    try:
        def getStartOfWeek(date: datetime) -> datetime:
            return date - timedelta(days=date.weekday())
        
        startDate = getStartOfWeek(startDate)
        weekRanges = []

        currentStart = startDate
        while currentStart < endDate:
            currentEnd = currentStart + timedelta(days=6, hours=23, minutes=59, seconds=59)
            if currentEnd > endDate:
                currentEnd = endDate
            
            weekRanges.append((int(currentStart.timestamp()), int(currentEnd.timestamp())))
            currentStart += timedelta(weeks=1)
        
        return weekRanges
    except Exception as error:
        LOGGER.error (f'Something went wrong, while getting week ranges with error: {error}')
        return []

# https://boosty.to/bazil.topol?isOnlyAllowedPosts=true&postsFrom=1722459600&postsTo=1724792399
# https://boosty.to/bazil.topol?isOnlyAllowedPosts=true&postsFrom=1727902800&postsTo=1728075599
def parseArticleURL(url: str) -> Article:
    try:
        LOGGER.info (f'Started parsing article by {url}')
        url = "https://boosty.to" + url
        DRIVER.get(url)
        return getArticleByHtml (DRIVER.page_source, url)
    except Exception as error:
        LOGGER.error (f'Something went wrong while parsing article: {url} with error: {error}')
        return None

def parseFeedURL(url: str) -> list:
    try:
        LOGGER.info (f'Started parsing feed of {url}')
        DRIVER.get (url)
        WebDriverWait(DRIVER, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "FeedFilter_root_mE0Y_")))
        time.sleep(10)
        soup = BeautifulSoup(DRIVER.page_source, 'html.parser')
        feed = soup.find ('div', class_="Feed_feed_CvVKF")

        articles = []
        for article in feed.find_all('div', class_="Feed_itemWrap_T5Uqp"):
            try:
                linkElement = article.find('a', class_="Link_defaultStyled_t7118")
                articleURL = linkElement.get('href')

                articleObj = parseArticleURL(articleURL)
                if articleObj is not None:
                    articles.append (articleObj)
            except Exception as error:
                LOGGER.error (f'Something went wring while parsing article: {article} with error: {error}')
        return articles
    except Exception as error:
        LOGGER.error (f'Something went wrong while parsing URL: {url} with error: {error}')
        return []

def parsePeriod(startDate: str, endDate: str, driver: WebDriver) -> list:
    try:
        LOGGER.info (f'Started parsing period startDate: {startDate}, endDate: {endDate}')

        global DRIVER
        DRIVER = driver

        startDate = datetime.strptime(startDate, "%d.%m.%Y")
        endDate = datetime.strptime(endDate, "%d.%m.%Y")

        weekRanges = getWeekRanges(startDate, endDate)
        generatedURLs = [URL_TEMPLATE.format(start, end) for start, end in weekRanges]
        LOGGER.info (f'Generated URLs: {generatedURLs}')

        parsedArticles = []
        for url in generatedURLs:
            parsedArticles.extend (parseFeedURL(url))
        LOGGER.info (f'Parsing period ended.')
        return parsedArticles
    except Exception as error:
        LOGGER.error (f'Something went wrong, while parsing period with error: {error}')
        return None